# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta, datetime
from django.utils.translation import ugettext as _
from simplehmis import consts

import logging
logger = logging.getLogger(__name__)


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
    name = models.TextField(db_index=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='projects')

    objects = ProjectManager()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ClientManager (models.Manager):
    def get_load_helper(self):
        from simplehmis.management.loader_utils import ClientLoaderHelper
        helper = ClientLoaderHelper()
        return helper

    def load_from_csv_file(self, filename):
        helper = self.get_load_helper()
        return helper.load_from_csv_file(self, filename)

    def get_or_create_client_from_row(self, row):
        helper = self.get_load_helper()
        return helper.get_or_create_client_from_row(self, row)

    def get_or_create_household_member_from_row(self, row):
        helper = self.get_load_helper()
        return helper.get_or_create_household_member_from_row(self, row)

    def get_or_create_assessments_from_row(self, row):
        helper = self.get_load_helper()
        return helper.get_or_create_assessments_from_row(self, row)

    def get_dump_helper(self):
        from simplehmis.management.dumper_utils import DumpHelper
        helper = DumpHelper()
        return helper

    def dump_to_csv_file(self, filename):
        helper = self.get_dump_helper()
        helper.dump_to_csv_file(
            self.prefetch_related('race'), filename,
            all_fields=('client_id', 'first', 'middle', 'last', 'suffix',
                        'dob', 'ssn','gender', 'race', 'ethnicity',
                        'veteran_status'),
            hud_code_fields={
                'gender': dict(consts.HUD_CLIENT_GENDER),
                'ethnicity': dict(consts.HUD_CLIENT_ETHNICITY),
                'veteran_status': dict(consts.HUD_YES_NO),
            },
            multi_hud_code_fields={'race'},
            renamed_fields={'client_id': 'id'}
        )


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

    first = models.CharField(_('First name'), max_length=100, blank=True, db_index=True)
    middle = models.CharField(_('Middle name'), max_length=100, blank=True, db_index=True)
    last = models.CharField(_('Last name'), max_length=100, blank=True, db_index=True)
    suffix = models.CharField(_('Name suffix'), max_length=100, blank=True)
    dob = models.DateField(_('Date of birth'), blank=True, null=True,
        help_text=_('Use the format YYYY-MM-DD (EX: 1972-07-01 for July 01, 1972)'))
    ssn = models.CharField(_('SSN'), max_length=9, blank=True, db_index=True,
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

    def get_dump_helper(self):
        from simplehmis.management.dumper_utils import HouseholdMemberDumpHelper
        helper = HouseholdMemberDumpHelper()
        return helper

    def dump_to_csv_file(self, filename):
        helper = self.get_dump_helper()
        helper.dump_to_csv_file(
            self.select_related('household__project'), filename,
            all_fields=('project_id', 'project_name', 'client_id',
                        'household_id', 'enrollment_id', 'hoh_relationship',
                        'entry_date', 'exit_date'),
            hud_code_fields={
                'hoh_relationship': dict(consts.HUD_CLIENT_HOH_RELATIONSHIP),
            },
            renamed_fields={'enrollment_id': 'id'}
        )


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
        return '{} Annual Assessment from {}'.format(self.member, self.assessment_date)


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
