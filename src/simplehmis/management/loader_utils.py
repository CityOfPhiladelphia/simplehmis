import csv

from django.utils.timezone import datetime
from simplehmis import consts
from simplehmis.models import ClientRace, Household, HouseholdMember, Project, ClientEntryAssessment, ClientExitAssessment

import logging
logger = logging.getLogger(__name__)


def hud_code(value, items):
    """
    Get the corresponding HUD code from a string value.
    """
    equivalents = {
        # Mapping sheet strings to equivalent consts strings
        'Permanent housing for formerly homeless persons': 'Permanent housing for formerly homeless persons (such as: CoC project; or HUD legacy programs; or HOPWA PH)',
        'Client Refused': 'Client refused',
        'Refused': 'Client refused',
        'Client doesn\'t know': 'Client doesn’t know',
        'Client Doesn’t Know': 'Client doesn’t know',
        'Client Doesn\'t Know': 'Client doesn’t know',
        'YES': 'Yes',
        'NO': 'No',

        # Destinations
        'Staying or living with friends, temporary tenure': 'Staying or living with friends, temporary tenure (e.g., room apartment or house)',
        'Staying or living  with friends, temporary tenure': 'Staying or living with friends, temporary tenure (e.g., room apartment or house)',
        'Staying or living  with friends, permanent tenure': 'Staying or living with friends, permanent tenure',
        'Staying or living in a family member\'s room, apartment or house': 'Staying or living in a family member’s room, apartment or house',
        'Staying or living in a friend\'s room, apartment or house': 'Staying or living in a friend’s room, apartment or house',
        'Staying or living with family, temporary tenure': 'Staying or living with family, temporary tenure (e.g., room, apartment or house)',
        'Place not meant for human habitation': 'Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)',
        'On the street or other place not meant for human habitation': 'Place not meant for habitation (e.g., a vehicle, an abandoned building, bus/train/subway station/airport or anywhere outside)',
        'Rental by client': 'Rental by client, no ongoing housing subsidy',
        'Permanent Housing': 'Permanent housing for formerly homeless persons (such as: CoC project; or HUD legacy programs; or HOPWA PH)',

        'Data Not Collected': 'Data not collected',
        'Jail, prison, or juvenile facility': 'Jail, prison or juvenile detention facility',
        '4': '4 or more',
        'Non-Hispanic / Non-Latino': 'Non-Hispanic/Non-Latino',
        'Non- Hispanic/Non-Latino': 'Non-Hispanic/Non-Latino',
        'Hispanic / Latino': 'Hispanic/Latino',
        'Hispanic': 'Hispanic/Latino',
        'Black': 'Black or African American',
        'Rental by client, no ongoing housing subsidy (Private Market)': 'Rental by client, no ongoing housing subsidy',
    }

    value = value.strip()

    for number, string in items:
        if string.lower() == value.lower():
            return number

        # As a special case, interpret the empty string as
        # "Data not collected" when "Data not collected" is
        # available as an option.
        if value.lower() == '' and string.lower() == 'data not collected':
            return number

        if equivalents.get(value) == string:
            return number

    raise KeyError('No value {!r} found'.format(value))


def parse_date(d):
    """
    Parse a mm/dd/yyyy date.
    """
    try:
        return datetime.strptime(d, '%m/%d/%Y').date() if d else None
    except ValueError:
        raise ValueError('Could not parse the date {!r}'.format(d))


def parse_ssn(ssn):
    """
    Remove extra dashes and spaces from an SSN.
    """
    ssn = ssn.replace('-', '').strip()
    if ssn.strip('0') == '':
        ssn = ''
    return ssn


class ClientLoaderHelper:
    """
    A helper class for a `ClientManager` to load data from a
    CSV file -- a fairly *ad hoc* process.

    """
    def load_from_csv_stream(self, manager, stream):
        reader = csv.DictReader(stream)
        rows = list(reader)

        # First create all the clients. We do the clients and households in
        # separate steps just in case any dependents are listed before the
        # head of household in the CSV.
        for row in rows:
            client, created = self.get_or_create_client_from_row(manager, row)
            logger.debug('{} client'.format('Created' if created else 'Updated'))

        # Next, for all those rows where a household member was not created,
        # create one.
        for row in rows:

            # If the member has been created and the SSN is blank, remember the
            # HOH. This remembered HOH will serve as the HOH for the subsequent
            # dependant household members.
            if '_member' in row:
                if row['_member'].client.ssn in ('', None) or row['_member'].client.ssn.strip('0') == '':
                    print('Storing HOH:', row['_member'])
                    self.remembered_hoh = row['_member']
                    self.remembered_entry_date = row['_member'].entry_date
                else:
                    self.remembered_hoh = None
                    self.remembered_entry_date = None

            elif '_member' not in row:
                self.get_or_create_household_member_from_row(manager, row)
                self.get_or_create_assessments_from_row(manager, row)

        return (row['_client'] for row in rows)

    def load_from_csv_file(self, manager, filename):
        logger.debug('Opening the CSV file {}'.format(filename))

        with open(filename, 'rU') as csvfile:
            return self.load_from_csv_stream(manager, csvfile)

    def get_or_create_client_from_row(self, manager, row):
        ssn = parse_ssn(row['SSN'])

        name_and_dob = dict(
            first=row['First Name'],
            last=row['Last Name'],
            dob=parse_date(row['DOB'])
        )

        client_values = dict(
            name_and_dob,
            ssn=ssn,
            middle=row['Middle Name'],
            ethnicity=hud_code(row['Ethnicity (HUD)'], consts.HUD_CLIENT_ETHNICITY),
            gender=hud_code(row['Gender (HUD)'], consts.HUD_CLIENT_GENDER),
            veteran_status=hud_code(row['Veteran Status (HUD)'], consts.HUD_YES_NO),
        )

        # Race, as a many-to-many field, gets applied separately.
        race = [
            hud_code(race, consts.HUD_CLIENT_RACE)
            for race in row['Race (HUD)'].split(';')
        ]

        def relaxed_get_or_create(defaults={}, **params):
            clients = manager.filter(**params)
            if len(clients) > 1:
                logger.warn('more than one client found for {}'.format(params))

            try:
                client = clients[0]
                created = False
            except IndexError:
                client = manager.create(**defaults)
                created = True

            return client, created

        # First, try to match on SSN
        if ssn:
            client, created = relaxed_get_or_create(ssn=ssn, defaults=client_values)

        # Failing that, try first, last, and date of birth
        elif all(name_and_dob.values()):
            client, created = relaxed_get_or_create(defaults=client_values, **name_and_dob)

        # Otherwise, just create a new client.
        else:
            client = manager.create(**client_values)
            created = True

        client.race = ClientRace.objects.filter(hud_value__in=race)
        row['_client'] = client

        client_changed = False
        for k, v in client_values.items():
            if getattr(client, k) != v:
                # If the value has gotten more specific, use the new value.
                if getattr(client, k) in (None, '', 99):
                    setattr(client, k, v)
                    client_changed = True

                # If the value has gotten less specific, ignore it.
                elif v in (None, '', 99):
                    pass

                # Otherwise, warn.
                else:
                    logger.warn('Warning: {} changed for client {} while loading from CSV: {!r} --> {!r}'.format(k, ssn, getattr(client, k), v))

        # The following only apply to clients that are listed as a head of
        # household.
        hoh_rel = row['Relationship to HoH']
        if hoh_rel == 'Self (head of household)':
            # Make sure that the HoH SSN matches the client's.
            hoh_ssn = parse_ssn(row['Head of Household\'s SSN'])
            assert ssn == hoh_ssn, \
                ('Client is listed as the head of household, but does not '
                 'match the head of household\'s SSN: {!r} vs {!r}: {}.'
                 ).format(ssn, hoh_ssn, row)

            # Check whether a household exists for this HoH's project and entry
            # date. If not, create one.
            self.get_or_create_household_member_from_row(manager, row)
            self.get_or_create_assessments_from_row(manager, row)

        return client, created

    def get_or_create_household_member_from_row(self, manager, row):
        client = row['_client']
        project_name = row['Program Name']
        entry_date = parse_date(row['Program Start Date'])
        exit_date = parse_date(row['Program End Date'])

        try:
            # If we can find a household membership that already exists for
            # this client in this project on this date, then use it
            # immediately.
            member = client.memberships.get(
                household__project__name=project_name,
                entry_date=entry_date)
            row['_member'] = member
            return member, False
        except HouseholdMember.DoesNotExist:
            pass

        if row['Relationship to HoH'] == 'Self (head of household)':
            # For heads of households, if we haven't found an existing
            # membership, then we can assume that we need to create a new
            # household.
            project, _ = Project.objects.get_or_create(name=project_name)
            household = Household.objects.create(project=project)
            ssn = parse_ssn(row['SSN'])

        else:
            # For dependants, we should use the household that exists for the
            # corresponding head of household.
            hoh_ssn = parse_ssn(row['Head of Household\'s SSN'])
            entry_date = parse_date(row['Program Start Date'])

            recall_hoh = (hoh_ssn == '')
            if recall_hoh:
                assert hasattr(self, 'remembered_hoh') and self.remembered_hoh is not None, 'Last seen HOH did not have a blank SSN; the current row does: {}.'.format(row)
                assert entry_date == self.remembered_entry_date, 'Entry dates for {} does not match recalled HOH -- {}'.format(row, self.remembered_hoh)
                hoh = self.remembered_hoh
            else:
                try:
                    hoh = HouseholdMember.objects.filter(client__ssn=hoh_ssn, entry_date__lte=entry_date).order_by('-entry_date')[0]
                except IndexError:
                    raise HouseholdMember.DoesNotExist('Could not find HOH with SSN {} and entry_date before {}'.format(hoh_ssn, entry_date))

            household = hoh.household
            is_hoh = False

        member = HouseholdMember.objects.create(
            client=client,
            household=household,
            hoh_relationship=hud_code(row['Relationship to HoH'], consts.HUD_CLIENT_HOH_RELATIONSHIP),
            entry_date=entry_date,
            exit_date=exit_date,
        )

        row['_member'] = member
        return member, True

    def get_or_create_assessments_from_row(self, manager, row):
        member = row['_member']
        entry_date = parse_date(row['Program Start Date'])
        exit_date = parse_date(row['Program End Date'])

        if 'never' in row['Exit Destination'].lower() or \
           'no show' in row['Exit Destination'].lower():
            # Treat clients with a destination including "never" as never
            # having shown up (there's no valid HUD destination code with
            # "never" in it).
            member.present_at_enrollment = False
            member.save()
            return None, None

        shared_values = dict(
            physical_disability=hud_code(row['Physical Disability'], consts.HUD_YES_NO),
            developmental_disability=hud_code(row['Developmental Disability'], consts.HUD_YES_NO),
            chronic_health=hud_code(row['Chronic Health Condition'], consts.HUD_YES_NO),
            hiv_aids=hud_code(row['HIV/AIDS'], consts.HUD_YES_NO),
            mental_health=hud_code(row['Mental Health Problem'], consts.HUD_YES_NO),
            substance_abuse=hud_code(row['Substance Abuse'], consts.HUD_CLIENT_SUBSTANCE_ABUSE),
            domestic_violence=hud_code(row['Domestic Violence'], consts.HUD_YES_NO),
        )

        entry_values = dict(
            shared_values,
            homeless_at_least_one_year=hud_code(row['Has Been Continuously Homeless (on the streets, in EH or in a Safe Haven) for at Least One Year'], consts.HUD_YES_NO),
            homeless_in_three_years=hud_code(row['Number of Times the Client has Been Homeless in the Past Three Years (streets, in EH, or in a safe haven)'], consts.HUD_CLIENT_HOMELESS_COUNT),
            prior_residence=hud_code(row['Residence Prior to Program Entry - Type of Residence'], consts.HUD_CLIENT_PRIOR_RESIDENCE),
            length_at_prior_residence=hud_code(row['Residence Prior to Program Entry - Length of Stay in Previous Place'], consts.HUD_CLIENT_LENGTH_AT_PRIOR_RESIDENCE),
        )

        exit_values = dict(
            shared_values,
            destination=hud_code(row['Exit Destination'], consts.HUD_CLIENT_DESTINATION),
        )

        # Get or create the entry and exit assessments, if there is an entry
        # or exit date, respectively. Spit a warning if there are different
        # values for the assessments.
        if entry_date:
            entry, _ = ClientEntryAssessment.objects.get_or_create(
                member=member,
                project_entry_date=entry_date,
                defaults=entry_values)
            for k, v in entry_values.items():
                if getattr(entry, k) != v:
                    logger.warn('Warning: {} changed for entry assessment on client {} while loading from CSV: {!r} --> {!r}'.format(k, entry.member, getattr(entry, k), v))
        else:
            entry = None

        if exit_date:
            exit, _ = ClientExitAssessment.objects.get_or_create(
                member=member,
                project_exit_date=exit_date,
                defaults=exit_values)
            for k, v in exit_values.items():
                if getattr(exit, k) != v:
                    logger.warn('Warning: {} changed for exit assessment on client {} while loading from CSV: {!r} --> {!r}'.format(k, exit.member, getattr(exit, k), v))
        else:
            exit = None

        return entry, exit
