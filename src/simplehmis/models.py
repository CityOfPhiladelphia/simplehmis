# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta, datetime
from django.utils.translation import ugettext as _
from simplehmis import consts

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
    return ssn.replace('-', '').strip()


class HMISUser (object):
    """
    A user object that adds a few convenience methods to the Django User.
    """
    def __init__(self, user):
        self.user = user
        self.groups = None

    def group_names(self):
        return (g.name for g in self.user.groups.all())

    def is_intake_staff(self):
        return 'intake-staff' in self.group_names()

    def is_project_staff(self):
        return 'project-staff' in self.group_names()

    def can_refer_household(self):
        user = self.user
        return user.is_superuser or user.has_perm('simplehmis.refer_household')

    def can_enroll_household(self):
        user = self.user
        return user.is_superuser or user.has_perm('simplehmis.enroll_household')

    def login_url(self, secure=False, host=None):
        from django.core.urlresolvers import reverse_lazy
        host = host or getattr(settings, 'SERVER_URL', None) or 'example.com'
        # view = reverse_lazy('login'),
        view = '/'

        return '%s://%s%s' % (
            'https' if secure else 'http',
            host,
            view[0]
        )

    def send_onboarding_email(self, secure=False, host=None):
        if not self.email:
            return

        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        subject = _('Welcome to SimpleHMIS')
        to_email = [self.email]
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'root@example.com')

        if self.is_superuser:
            staff_type = 'a site-wide administrator'
        elif self.is_project_staff():
            staff_type = 'a project staff member for {}'.format(', '.join(p.name for p in self.projects.all()))
        elif self.is_intake_staff():
            staff_type = 'an intake staff member'
        else:
            staff_type = 'a site staff member'

        context = {
            'login_url': self.login_url(secure=secure, host=host),
            'username': self.username,
            'staff_type': staff_type,
            'help_email': getattr(settings, 'HELP_EMAIL', 'help@example.com'),
        }

        text_content = render_to_string('onboarding_email.txt', context)
        html_content = render_to_string('onboarding_email.html', context)

        send_mail(subject, text_content, from_email, to_email, html_message=html_content)

    def __getattr__(self, key):
        return getattr(self.user, key)

    def __dir__(self):
        return dir(self.user) + super().__dir__()


class TimestampedModel (models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProjectManager (models.Manager):
    def create_from_csv_file(self, filename):
        import csv
        logger.debug('Opening the CSV file {}'.format(filename))
        with open(filename, 'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            projects = [Project(name=row['ProjectName']) for row in reader]
            logger.debug('Creating {} projects'.format(len(projects)))
            return self.bulk_create(projects)


class Project (TimestampedModel):
    name = models.TextField()
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='projects')

    objects = ProjectManager()

    def __str__(self):
        return self.name


class ClientManager (models.Manager):
    def load_from_csv_file(self, filename):
        import csv
        logger.debug('Opening the CSV file {}'.format(filename))

        with open(filename, 'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            # First create all the clients. We do the clients and households in
            # separate steps just in case any dependents are listed before the
            # head of household in the CSV.
            for row in rows:
                client, created = self.get_or_create_client_from_row(row)
                logger.debug('{} client'.format('Created' if created else 'Updated'))

            # Next, for all those rows where a household member was not created,
            # create one.
            for row in rows:
                if '_member' not in row:
                    self.get_or_create_household_member_from_row(row)
                    self.get_or_create_assessments_from_row(row)

            return (row['_client'] for row in rows)

    def get_or_create_client_from_row(self, row):
        ssn = parse_ssn(row['SSN'])

        name_and_dob = dict(
            first=row['First Name'],
            last=row['Last Name'],
            dob=parse_date(row['DOB'])
        )

        client_values = dict(
            name_and_dob,
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

        # First, try to match on SSN
        if ssn:
            client, created = self.get_or_create(ssn=ssn, defaults=client_values)

        # Failing that, try first, last, and date of birth
        elif all(name_and_dob.values()):
            client, created = self.get_or_create(defaults=client_values, **name_and_dob)

        # Otherwise, just create a new client.
        else:
            client = self.create(ssn=ssn, **client_values)
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
                 'match the head of household\'s SSN: {!r} vs {!r}.'
                 ).format(ssn, hoh_ssn)

            # Check whether a household exists for this HoH's project and entry
            # date. If not, create one.
            self.get_or_create_household_member_from_row(row)
            self.get_or_create_assessments_from_row(row)

        return client, created

    def get_or_create_household_member_from_row(self, row):
        client = row['_client']
        project_name = row['Program Name']
        entry_date = parse_date(row['Program Start Date'])

        try:
            # If we can find a household membership that already exists for
            # this client in this project on this date, then use it
            # immediately.
            member = client.memberships.get(
                household__project__name=project_name,
                entry_assessment__project_entry_date=entry_date)
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
        else:
            # For dependants, we should use the household that exists for the
            # corresponding head of household.
            hoh_ssn = parse_ssn(row['Head of Household\'s SSN'])
            entry_date=parse_date(row['Program Start Date'])
            hoh = HouseholdMember.objects.get(client__ssn=hoh_ssn, entry_assessment__project_entry_date=entry_date)
            household = hoh.household

        member = HouseholdMember.objects.create(
            client=client,
            household=household,
            hoh_relationship=hud_code(row['Relationship to HoH'], consts.HUD_CLIENT_HOH_RELATIONSHIP)
        )
        row['_member'] = member
        return member, True

    def get_or_create_assessments_from_row(self, row):
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


class ClientRace (models.Model):
    label = models.CharField(max_length=100)
    hud_value = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return self.label


class Client (TimestampedModel):
    """
    The Client object contains all those data elements in the HMIS Data
    Dictionary that have a "Universal" element type, and a "Record Creation"
    collection point.

    - Element Type = Universal
    - Collection Point = Record Creation
    """

    first = models.CharField(_('First name'), max_length=100, blank=True)
    middle = models.CharField(_('Middle name'), max_length=100, blank=True)
    last = models.CharField(_('Last name'), max_length=100, blank=True)
    suffix = models.CharField(_('Name suffix'), max_length=100, blank=True)
    dob = models.DateField(_('Date of birth'), blank=True, null=True,
        help_text=_('Use the format YYYY-MM-DD (EX: 1972-07-01 for July 01, 1972)'))
    ssn = models.CharField(_('SSN'), max_length=9, blank=True,
        help_text=_('Enter 9 digit SSN Do not enter hyphens EX: 555210987'))
    gender = models.PositiveIntegerField(_('Gender'), blank=True, null=True, choices=consts.HUD_CLIENT_GENDER, default=consts.HUD_BLANK)
    other_gender = models.TextField(_('If "Other" for gender, please specify'), blank=True)
    ethnicity = models.PositiveIntegerField(_('Ethnicity'), blank=True, null=True, choices=consts.HUD_CLIENT_ETHNICITY, default=consts.HUD_BLANK)
    race = models.ManyToManyField(ClientRace, verbose_name=_('Race'), blank=True, default=consts.HUD_BLANK)
    # TODO: veteran status field should not validate if it conflicts with the
    #       client's age.
    veteran_status = models.PositiveIntegerField(_('Veteran status (adults only)'), blank=True, null=True, choices=consts.HUD_YES_NO, default=consts.HUD_BLANK,
        help_text=_('Only collect veteran status if client is over 18.'))

    objects = ClientManager()

    def name_display(self):
        name_pieces = []
        if self.first: name_pieces.append(self.first)
        if self.middle: name_pieces.append(self.middle)
        if self.last: name_pieces.append(self.last)
        if self.suffix: name_pieces.append(self.suffix)

        return ' '.join(name_pieces)
    name_display.short_description = _('Name')

    def ssn_display(self):
        # TODO: When should we show a full SSN?
        return '***-**-' + self.ssn[-4:] if self.ssn else ''
    ssn_display.short_description = _('Social Security')

    def is_adult(self):
        return (self.dob) and (now() - self.dob > timedelta(years=18))

    def __str__(self):
        return '{} (SSN: {})'.format(self.name_display(), self.ssn_display())


class HouseholdManager (models.QuerySet):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('members')

    def filter_by_enrollment(self, status):
        """
        status can be:
        -1 -- Has not yet been fully enrolled in a program
        0  -- Is currently at least partially enrolled in a program
        1  -- Has completely exited a program
        """
        from django.db.models import Count, F, Q
        if status is None:
            return self

        status = str(status)
        if status == '-1':
            qs = self\
                .filter(members__present_at_enrollment=True)\
                .annotate(total_member_count=Count('members'))\
                .annotate(enrolled_count=Count('members__entry_date'))\
                .filter(enrolled_count__lt=F('total_member_count'))
        elif status == '0':
            qs = self\
                .filter(members__present_at_enrollment=True)\
                .annotate(total_member_count=Count('members'))\
                .annotate(enrolled_count=Count('members__entry_date'))\
                .annotate(exited_count=Count('members__exit_date'))\
                .filter(enrolled_count=F('total_member_count'))\
                .filter(exited_count__lt=F('total_member_count'))
        elif status == '1':
            qs = self\
                .filter(members__present_at_enrollment=True)\
                .annotate(total_member_count=Count('members'))\
                .annotate(exited_count=Count('members__exit_date'))\
                .filter(exited_count=F('total_member_count'))
        else:
            raise ValueError('Status should only be one of -1, 0, or 1. Got {}'.format(status))
        return qs


class Household (TimestampedModel):
    """
    3.14   Household ID
    -------------------

    A Household ID will be assigned to each household at each project entry and
    applies for the duration of that project stay to all members of the
    household served.  The Household ID must be automatically generated by the
    HMIS application to  ensure that it is unique. The Household ID has no
    meaning beyond a single  enrollment; it is used in conjunction with the
    Project ID, Project Entry Date, and  Project Exit Date to link records for
    household members together and indicate that  they were served together.

    The Household ID is to be unique to the household stay in a project; reuse
    of the  identification for the same or similar household upon readmission
    into the project is  unacceptable.

    """
    project = models.ForeignKey('Project', null=True)
    referral_notes = models.TextField(_('Referral notes'), blank=True)

    objects = HouseholdManager.as_manager()

    class Meta:
        permissions = [
            ('refer_household', 'Can refer household to a project'),
            ('enroll_household', 'Can enroll household in a project'),
        ]
        verbose_name = _('household referral')
        verbose_name_plural = _('household referrals')

    def member_count(self):
        return len(self.members.all())
    member_count.short_description = _('# of members in household')

    def members_display(self):
        return ',\n'.join(str(m) for m in self.members.all())
    members_display.short_description = _('Household composition')

    def hoh(self):
        try: return self.members.all()[0]
        except IndexError: return None
    hoh.short_description = _('Head of household')

    def dependents(self):
        return self.members.all()[1:]

    def dependents_display(self):
        return ', '.join(str(m) for m in self.dependents())
    dependents_display.short_description = _('Dependents')

    def is_enrolled(self):
        members = self.members.all()

        # If any present member is pending, then the whole
        # household is pending
        for member in members:
            if member.present_at_enrollment:
                if member.is_enrolled() is None:
                    return None

        # If none are pending, then if any member is
        # enrolled, then the whole household is enrolled.
        for member in members:
            if member.present_at_enrollment:
                if member.is_enrolled() is True:
                    return True

        # If no one present is pending or enrolled, then
        # The whole household is exited.
        return False
    is_enrolled.boolean = True

    def date_of_entry(self):
        hoh = self.hoh()
        if hoh:
            return hoh.project_entry_date()
    date_of_entry.short_description = _('Date of entry')
    date_of_entry.admin_order_field = 'members__entry_assessment__project_entry_date'

    def __str__(self):
        return '{}\'s household'.format(self.hoh())


class HouseholdMemberQuerySet (models.QuerySet):
    def filter_by_enrollment(self, status):
        """
        status can be:
        -1 -- Has not yet ben enrolled in a program
        0  -- Is currently enrolled in a program
        1  -- Has exited a program
        """
        if status is None:
            return self

        status = str(status)
        if status == '-1':
            qs = self\
                .filter(present_at_enrollment=True)\
                .filter(entry_date__isnull=True)
        elif status == '0':
            qs = self\
                .filter(present_at_enrollment=True)\
                .filter(exit_date__isnull=True)\
                .filter(entry_date__isnull=False)
        elif status == '1':
            qs = self\
                .filter(present_at_enrollment=True)\
                .filter(exit_date__isnull=False)
        else:
            raise ValueError('Status should only be one of -1, 0, or 1. Got {}'.format(status))
        return qs


class HouseholdMember (TimestampedModel):
    """
    3.14   Household ID
    -------------------
    ...(cont'd)

    Persons may join a household with members who have already begun a project
    entry or may leave a project although other members of the household remain
    in the project. A common Household ID must be assigned to each member of the
    same household. Persons in a household (either adults or children) who are
    not present when the household initially applies for assistance and later
    join the household should be assigned the same Household ID that links them
    to the rest of the persons in the household. The early departure of a
    household member would have no impact on the Household ID.

    """
    client = models.ForeignKey('Client', related_name='memberships')
    household = models.ForeignKey('Household', related_name='members')

    # 3.15   Relationship to Head of Household
    # ----------------------------------------
    #
    # The term Head of Household is not intended to mean the leader of the
    # house, rather it is to identify one client by which to attach the other
    # household members.

    hoh_relationship = models.PositiveIntegerField(_('Relationship to head of household'), choices=consts.HUD_CLIENT_HOH_RELATIONSHIP)
    present_at_enrollment = models.BooleanField(_('Present?'), default=True)

    entry_date = models.DateField(null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)

    objects = HouseholdMemberQuerySet.as_manager()

    class Meta:
        ordering = ['hoh_relationship']

    def __str__(self):
        return str(self.client)

    def project(self):
        return self.household.project
    project.short_description = _('Project')

    def project_entry_date(self):
        try: return self.entry_assessment.project_entry_date
        except ClientEntryAssessment.DoesNotExist: return None
    project_entry_date.short_description = _('Entry Date')
    project_entry_date.admin_order_field = 'entry_assessment__project_entry_date'

    def project_exit_date(self):
        try: return self.exit_assessment.project_exit_date
        except ClientExitAssessment.DoesNotExist: return None
    project_exit_date.short_description = _('Exit Date')
    project_exit_date.admin_order_field = 'exit_assessment__project_exit_date'

    def has_entered(self):
        return self.entry_date is not None

    def has_exited(self):
        return self.exit_date is not None

    def is_enrolled(self):
        if not self.present_at_enrollment:
            return False
        if not self.has_entered():
            return None
        if not self.has_exited():
            return True
        else:
            return False
        return self.has_entered() and not self.has_exited()
    is_enrolled.boolean = True

    def has_entry_assessment(self):
        try:
            self.entry_assessment
            return True
        except ClientEntryAssessment.DoesNotExist:
            return False

    def has_exit_assessment(self):
        try:
            self.exit_assessment
            return True
        except ClientExitAssessment.DoesNotExist:
            return False


class HealthInsuranceFields (models.Model):
    """
    4.4   Health Insurance
    ----------------------

    """
    health_insurance = models.PositiveIntegerField(_('Client has health insurance'), choices=consts.HUD_YES_NO, default=consts.HUD_BLANK, null=True)
    health_insurance_medicaid = models.PositiveIntegerField(_('MEDICAID'), choices=consts.YES_NO, default=0)
    health_insurance_medicare = models.PositiveIntegerField(_('MEDICARE'), choices=consts.YES_NO, default=0)
    health_insurance_chip = models.PositiveIntegerField(_('State Children’s Health Insurance Program (or use local name)'), choices=consts.YES_NO, default=0)
    health_insurance_va = models.PositiveIntegerField(_('Veteran’s Administration (VA) Medical Services'), choices=consts.YES_NO, default=0)
    health_insurance_employer = models.PositiveIntegerField(_('Employer – Provided Health Insurance'), choices=consts.YES_NO, default=0)
    health_insurance_cobra = models.PositiveIntegerField(_('Health Insurance obtained through COBRA'), choices=consts.YES_NO, default=0)
    health_insurance_private = models.PositiveIntegerField(_('Private Pay Health Insurance'), choices=consts.YES_NO, default=0)
    health_insurance_state = models.PositiveIntegerField(_('State Health Insurance for Adults (or use local name)'), choices=consts.YES_NO, default=0)
    # TODO: This next is HOPWA-only; should we omit?
    health_insurance_none_reason = models.PositiveIntegerField(_('If none of the above, give reason'), choices=consts.HUD_CLIENT_UNINSURED_REASON, default=consts.HUD_BLANK, blank=True, null=True)

    class Meta:
        abstract = True


class DisablingConditionFields (models.Model):
    """
    3.8   Disabling Condition
    -------------------------

    Disabling Condition directly relates to the Program-Specific Elements
    capturing more detailed information on Special Needs: Physical Disability,
    Developmental Disability, Chronic Health Condition, HIV/AIDS, Mental
    Health Problem, and/or Substance Abuse. If all of the Special Needs
    elements are present for completion in the HMIS application for a
    particular project then disabling condition may be inferred to be “yes”
    from an answer of “yes” to the dependent field in those elements “expected
    to be of long–continued and indefinite duration and substantially impairs
    ability to live independently”. Disabling condition may either be entered
    by the user independently of any other special need field, or data in this
    field may be inferred by the responses to “ability to live independently”.
    If any one of these is “yes” then disabling condition should also be
    “yes”.

    4.5   Physical Disability
    4.6   Developmental Disability
    4.7   Chronic Health Condition
    4.8   HIV/AIDS
    4.9   Mental Health Problems
    4.10  Substance Abuse

    """
    physical_disability = models.PositiveIntegerField(_('Does the client have a physical disability?'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    physical_disability_impairing = models.PositiveIntegerField(_('If yes, is the physical disability expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)
    developmental_disability = models.PositiveIntegerField(_('Does the client have a developmental disability?'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    developmental_disability_impairing = models.PositiveIntegerField(_('If yes, is the developmental disability expected to substantially impair ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)
    chronic_health = models.PositiveIntegerField(_('Does the client have a chronic health condition?'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    chronic_health_impairing = models.PositiveIntegerField(_('If yes, is the chronic health condition expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)
    hiv_aids = models.PositiveIntegerField(_('Does the client have HIV/AIDS?'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    hiv_aids_impairing = models.PositiveIntegerField(_('If yes, is HIV/AIDS expected to substantially impair ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)
    mental_health = models.PositiveIntegerField(_('Does the client have a mental health problem?'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    mental_health_impairing = models.PositiveIntegerField(_('If yes, is the mental health problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)
    substance_abuse = models.PositiveIntegerField(_('Does the client have a substance abuse problem?'), choices=consts.HUD_CLIENT_SUBSTANCE_ABUSE, null=True, default=consts.HUD_BLANK)
    substance_abuse_impairing = models.PositiveIntegerField(_('If yes for alcohol abuse, drug abuse, or both, is the substance abuse problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_BLANK)

    @property
    def disabling_condition(self):
        def eq(val):
            return lambda item: item == val

        disability_fields = (
            self.physical_disability,
            self.developmental_disability,
            self.chronic_health,
            self.hiv_aids,
            self.mental_health,
            self.substance_abuse,
        )

        impairing_fields = (
            self.physical_disability_impairing,
            self.developmental_disability_impairing,
            self.chronic_health_impairing,
            self.hiv_aids_impairing,
            self.mental_health_impairing,
            self.substance_abuse_impairing,
        )

        if all(eq(0), disability_fields):
            return 0
        if all(eq(0), impairing_fields):
            return 0
        for val in (1, 8, 9, 99):
            if any(eq(val), impairing_fields):
                return val

    class Meta:
        abstract = True


class HousingStatusFields (models.Model):
    """
    4.1   Housing Status
    3.17  Length of Time on Street, in an Emergency Shelter, or Safe Haven
    3.9   Residence Prior to Project Entry

    Data collection is required for all Head of Households and adult household
    members, which will require collection for at least one member of a
    household comprised of only children.

    """
    housing_status = models.PositiveIntegerField(_('Housing status'), choices=consts.HUD_CLIENT_HOUSING_STATUS, null=True, default=consts.HUD_BLANK)

    homeless_at_least_one_year = models.PositiveIntegerField(_('Continuously homeless for at least one year'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    homeless_in_three_years = models.PositiveIntegerField(_('Number of times the client has been homeless in the past three years'), choices=consts.HUD_CLIENT_HOMELESS_COUNT, null=True, default=consts.HUD_BLANK)
    homeless_months_in_three_years = models.PositiveIntegerField(_('If client has been homeless 4 or more times, how many total months homeless in the past three years'), choices=consts.HUD_CLIENT_HOMELESS_MONTHS, blank=True, null=True, default=consts.HUD_BLANK)
    homeless_months_prior = models.PositiveIntegerField(_('Total number of months continuously homeless immediately prior to project entry (partial months should be rounded UP)'), null=True)
    status_documented = models.PositiveIntegerField(choices=consts.YES_NO, blank=True, null=True)
    # TODO: WHAT DOES status_documented MEAN?

    prior_residence = models.PositiveIntegerField(_('Type of residence prior to project entry'), choices=consts.HUD_CLIENT_PRIOR_RESIDENCE, null=True, default=consts.HUD_BLANK)
    prior_residence_other = models.TextField(_('If "Other" for type of residence, specify where'), blank=True)
    length_at_prior_residence = models.PositiveIntegerField(_('Length of time at prior residence'), choices=consts.HUD_CLIENT_LENGTH_AT_PRIOR_RESIDENCE, null=True, default=consts.HUD_BLANK)

    class Meta:
        abstract = True


class IncomeFields (models.Model):
    """
    4.2   Income and Sources

    """
    income_status = models.PositiveIntegerField(_('Income from any source?'), null=True, choices=consts.HUD_YES_NO, default=consts.HUD_BLANK)
    income_notes = models.TextField(_('Note all sources and dollar amounts for each source.'), blank=True)

    class Meta:
        abstract = True


class DomesticViolenceFields (models.Model):
    """
    4.11   Domestic Violence
    ------------------------

    """
    domestic_violence = models.PositiveIntegerField(_('Client is a victim/survivor of domestic violence'), choices=consts.HUD_YES_NO, null=True, default=consts.HUD_BLANK)
    domestic_violence_occurred = models.PositiveIntegerField(_('If Client has experience domestic violence, when?'), choices=consts.HUD_CLIENT_DOMESTIC_VIOLENCE, blank=True, null=True, default=consts.HUD_BLANK)

    class Meta:
        abstract = True


class DestinationFields (models.Model):
    """
    3.12   Destination
    ------------------

    """
    destination = models.PositiveIntegerField(choices=consts.HUD_CLIENT_DESTINATION, null=True)
    destination_other = models.TextField(blank=True)

    class Meta:
        abstract = True


class ClientEntryAssessment (TimestampedModel, HealthInsuranceFields,
    DisablingConditionFields, HousingStatusFields, DomesticViolenceFields, IncomeFields):
    """
    Contains all those data elements in the HMIS Data Dictionary that have a
    "Universal" element type, and a "Project Entry" collection point.

    - Element Type = Universal
    - Collection Point = Project Entry
    """
    member = models.OneToOneField('HouseholdMember', related_name='entry_assessment')
    project_entry_date = models.DateField(null=True,
        help_text=_('Note that you MUST set an entry date for a client to be enrolled.'))

    class Meta:
        verbose_name_plural = _('Client entry assessment')

    def __str__(self):
        return '{} Entry Information'.format(self.member)


class ClientAnnualAssessment (TimestampedModel, HealthInsuranceFields,
    DisablingConditionFields, DomesticViolenceFields, IncomeFields):
    """
    The ClientExitInformation object contains all those data elements in the
    HMIS Data Dictionary that have a "Universal" element type, and a "Project
    Entry" collection point.

    - Element Type = Universal
    - Collection Point = Annual Assessment
    """
    member = models.ForeignKey('HouseholdMember', related_name='annual_assessments')
    assessment_date = models.DateField(default=now)

    def __str__(self):
        return '{} Annual Assessment from {}'.format(self.member, self.collected_at)


class ClientExitAssessment (TimestampedModel, HealthInsuranceFields,
    DisablingConditionFields, DomesticViolenceFields, IncomeFields, DestinationFields):
    """
    Contains all those data elements in the HMIS Data Dictionary that have a
    "Universal" element type, and a "Project Entry" collection point.

    - Element Type = Universal
    - Collection Point = Project Exit
    """
    member = models.OneToOneField('HouseholdMember', related_name='exit_assessment')
    project_exit_date = models.DateField()

    def __str__(self):
        return '{} Exit Information'.format(self.member)
