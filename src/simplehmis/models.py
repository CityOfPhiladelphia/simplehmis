# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta
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
    dob = models.DateField(_('Date of birth'), blank=True, null=True)
    ssn = models.CharField(_('SSN'), max_length=9, blank=True,
        help_text=_('Enter 9 digit SSN Do not enter hyphens EX: 555210987'))
    gender = models.PositiveIntegerField(_('Gender'), blank=True, null=True, choices=consts.HUD_CLIENT_GENDER, default=consts.HUD_DATA_NOT_COLLECTED)
    other_gender = models.TextField(_('If "Other" for gender, please specify'), blank=True)
    ethnicity = models.PositiveIntegerField(_('Ethnicity'), blank=True, null=True, choices=consts.HUD_CLIENT_ETHNICITY, default=consts.HUD_DATA_NOT_COLLECTED)
    race = models.PositiveIntegerField(_('Race'), blank=True, null=True, choices=consts.HUD_CLIENT_RACE, default=consts.HUD_DATA_NOT_COLLECTED)
    # TODO: veteran status field should not validate if it conflicts with the
    #       client's age.
    veteran_status = models.PositiveIntegerField(_('Veteran status (adults only)'), blank=True, null=True, choices=consts.HUD_YES_NO, default=consts.HUD_DATA_NOT_COLLECTED,
        help_text=_('Only collect veteran status if client is over 18.'))

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


class HouseholdManager (models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('members')


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
    project = models.ForeignKey('Project', null=True, blank=True)
    referral_notes = models.TextField(_('Referral notes'), blank=True)

    objects = HouseholdManager()

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
        return ', '.join(str(m) for m in self.members.all())
    members_display.short_description = _('Members in household')

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
        return any(member.is_enrolled() for member in self.members.all())
    is_enrolled.boolean = True

    def __str__(self):
        return '{}\'s household'.format(self.hoh())


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
    present_at_enrollment = models.BooleanField(_('Present at enrollment'), default=True)

    class Meta:
        ordering = ['hoh_relationship']

    def __str__(self):
        return str(self.client)

    def has_entered(self):
        try: return self.entry_assessment is not None
        except ClientEntryAssessment.DoesNotExist: return False

    def has_exited(self):
        try: return self.exit_assessment is not None
        except ClientExitAssessment.DoesNotExist: return False

    def is_enrolled(self):
        return self.has_entered() and not self.has_exited()
    is_enrolled.boolean = True


class HealthInsuranceFields (models.Model):
    """
    4.4   Health Insurance
    ----------------------

    """
    health_insurance = models.PositiveIntegerField(_('Client has health insurance'), choices=consts.HUD_YES_NO, default=consts.HUD_DATA_NOT_COLLECTED, blank=True, null=True)
    health_insurance_medicaid = models.PositiveIntegerField(_('MEDICAID'), choices=consts.YES_NO, default=0)
    health_insurance_medicare = models.PositiveIntegerField(_('MEDICARE'), choices=consts.YES_NO, default=0)
    health_insurance_chip = models.PositiveIntegerField(_('State Children’s Health Insurance Program (or use local name)'), choices=consts.YES_NO, default=0)
    health_insurance_va = models.PositiveIntegerField(_('Veteran’s Administration (VA) Medical Services'), choices=consts.YES_NO, default=0)
    health_insurance_employer = models.PositiveIntegerField(_('Employer – Provided Health Insurance'), choices=consts.YES_NO, default=0)
    health_insurance_cobra = models.PositiveIntegerField(_('Health Insurance obtained through COBRA'), choices=consts.YES_NO, default=0)
    health_insurance_private = models.PositiveIntegerField(_('Private Pay Health Insurance'), choices=consts.YES_NO, default=0)
    health_insurance_state = models.PositiveIntegerField(_('State Health Insurance for Adults (or use local name)'), choices=consts.YES_NO, default=0)
    # TODO: This next is HOPWA-only; should we omit?
    health_insurance_none_reason = models.PositiveIntegerField(_('If none of the above, give reason'), choices=consts.HUD_CLIENT_UNINSURED_REASON, default=consts.HUD_DATA_NOT_COLLECTED, blank=True, null=True)

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
    physical_disability = models.PositiveIntegerField(_('Physical disability'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    physical_disability_impairing = models.PositiveIntegerField(_('If yes, is the physical disability expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    developmental_disability = models.PositiveIntegerField(_('Developmental disability'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    developmental_disability_impairing = models.PositiveIntegerField(_('If yes, is the developmental disability expected to substantially impair ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    chronic_health = models.PositiveIntegerField(_('Chronic health condition'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    chronic_health_impairing = models.PositiveIntegerField(_('If yes, is the chronic health condition expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    hiv_aids = models.PositiveIntegerField(_('HIV/AIDS'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    hiv_aids_impairing = models.PositiveIntegerField(_('If yes, is HIV/AIDS expected to substantially impair ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    mental_health = models.PositiveIntegerField(_('Mental health problem'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    mental_health_impairing = models.PositiveIntegerField(_('If yes, is the mental health problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    substance_abuse = models.PositiveIntegerField(_('Substance abuse problem'), choices=consts.HUD_CLIENT_SUBSTANCE_ABUSE, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    substance_abuse_impairing = models.PositiveIntegerField(_('If yes for alcohol abuse, drug abuse, or both, is the substance abuse problem expected to be of long–continued and indefinite duration and substantially impairs ability to live independently'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)

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
    housing_status = models.PositiveIntegerField(_('Housing status'), choices=consts.HUD_CLIENT_HOUSING_STATUS, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)

    homeless_at_least_one_year = models.PositiveIntegerField(_('Continuously homeless for at least one year'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    homeless_in_three_years = models.PositiveIntegerField(_('Number of times the client has been homeless in the past three years'), choices=consts.HUD_CLIENT_HOMELESS_COUNT, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    homeless_months_in_three_years = models.PositiveIntegerField(_('Total number of months homeless in the past three years, if homeless 4 or more times'), choices=consts.HUD_CLIENT_HOMELESS_MONTHS, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    homeless_months_prior = models.PositiveIntegerField(_('Total number of months continuously homeless immediately prior to project entry (partial months should be rounded UP)'), blank=True, null=True)
    status_documented = models.PositiveIntegerField(choices=consts.YES_NO, blank=True, null=True)
    # TODO: WHAT DOES status_documented MEAN?

    prior_residence = models.PositiveIntegerField(_('Type of residence prior to project entry'), choices=consts.HUD_CLIENT_PRIOR_RESIDENCE, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    prior_residence_other = models.TextField(_('If Other for type of residence, specify where'), blank=True)
    length_at_prior_residence = models.PositiveIntegerField(_('Length of time at prior residence'), choices=consts.HUD_CLIENT_LENGTH_AT_PRIOR_RESIDENCE, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)

    class Meta:
        abstract = True


class DomesticViolenceFields (models.Model):
    """
    4.11   Domestic Violence
    ------------------------

    """
    domestic_violence = models.PositiveIntegerField(_('Client is a victim/survivor of domestic violence'), choices=consts.HUD_YES_NO, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)
    domestic_violence_occurred = models.PositiveIntegerField(_('If Client has experience domestic violence, when?'), choices=consts.HUD_CLIENT_DOMESTIC_VIOLENCE, blank=True, null=True, default=consts.HUD_DATA_NOT_COLLECTED)

    class Meta:
        abstract = True


class DestinationFields (models.Model):
    """
    3.12   Destination
    ------------------

    """
    destination = models.PositiveIntegerField(choices=consts.HUD_CLIENT_DESTINATION, null=True, blank=True)
    destination_other = models.TextField(blank=True)

    class Meta:
        abstract = True


class ClientEntryAssessment (TimestampedModel, HealthInsuranceFields,
    DisablingConditionFields, HousingStatusFields, DomesticViolenceFields):
    """
    Contains all those data elements in the HMIS Data Dictionary that have a
    "Universal" element type, and a "Project Entry" collection point.

    - Element Type = Universal
    - Collection Point = Project Entry
    """
    member = models.OneToOneField('HouseholdMember', related_name='entry_assessment')
    project_entry_date = models.DateField(null=True)

    class Meta:
        verbose_name_plural = _('Client entry assessment')

    def __str__(self):
        return '{} Entry Information'.format(self.member)


class ClientAnnualAssessment (TimestampedModel, HealthInsuranceFields,
    DisablingConditionFields, DomesticViolenceFields):
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
    DisablingConditionFields, DomesticViolenceFields, DestinationFields):
    """
    Contains all those data elements in the HMIS Data Dictionary that have a
    "Universal" element type, and a "Project Entry" collection point.

    - Element Type = Universal
    - Collection Point = Project Exit
    """
    member = models.OneToOneField('HouseholdMember', related_name='exit_assessment')
    project_exit_date = models.DateField(default=now)

    def __str__(self):
        return '{} Exit Information'.format(self.member)
