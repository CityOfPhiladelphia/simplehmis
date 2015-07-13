# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _


YES_NO = (
    (0, _('No')),
    (1, _('Yes')),
)


PROJECT_TYPE_CHOICES = (
    (1, _('Emergency Shelter')),
    (2, _('Transitional Housing')),
    (3, _('PH - Permanent Supportive Housing (disability required for entry)')),
    (4, _('Street Outreach')),
    (5, _('RETIRED')),
    (6, _('Services Only')),
    (7, _('Other')),
    (8, _('Safe Haven')),
    (9, _('PH – Housing Only')),
    (10, _('PH – Housing with Services (no disability required for entry)')),
    (11, _('Day Shelter')),
    (12, _('Homelessness Prevention')),
    (13, _('PH - Rapid Re-Housing')),
    (14, _('Coordinated Assessment')),
)


PROJECT_TRACKING_METHOD_CHOICES = (
    (0, _('Entry/Exit Date')),
    (3, _('Night-by-Night')),
)


FUNDING_PROGRAM_CHOICES = (
    (1, _('HUD:CoC – Homelessness Prevention (High Performing Comm. Only)')),
    (2, _('HUD:CoC – Permanent Supportive Housing ')),
    (3, _('HUD:CoC – Rapid Re-Housing')),
    (4, _('HUD:CoC – Supportive Services Only')),
    (5, _('HUD:CoC – Transitional Housing')),
    (6, _('HUD:CoC – Safe Haven')),
    (7, _('HUD:CoC – Single Room Occupancy (SRO)')),
    (8, _('HUD:ESG – Emergency Shelter (operating and/or essential services)')),
    (9, _('HUD:ESG – Homelessness Prevention ')),
    (10, _('HUD:ESG – Rapid Rehousing')),
    (11, _('HUD:ESG – Street Outreach')),
    (12, _('HUD:Rural Housing Stability Assistance Program ')),
    (13, _('HUD:HOPWA – Hotel/Motel Vouchers')),
    (14, _('HUD:HOPWA – Housing Information')),
    (15, _('HUD:HOPWA – Permanent Housing (facility based or TBRA)')),
    (16, _('HUD:HOPWA – Permanent Housing Placement ')),
    (17, _('HUD:HOPWA – Short-Term Rent, Mortgage, Utility assistance')),
    (18, _('HUD:HOPWA – Short-Term Supportive Facility')),
    (19, _('HUD:HOPWA – Transitional Housing (facility based or TBRA)')),
    (20, _('HUD:HUD/VASH')),
    (21, _('HHS:PATH – Street Outreach & Supportive Services Only')),
    (22, _('HHS:RHY – Basic Center Program (prevention and shelter)')),
    (23, _('HHS:RHY – Maternity Group Home for Pregnant and Parenting Youth')),
    (24, _('HHS:RHY – Transitional Living Program')),
    (25, _('HHS:RHY – Street Outreach Project')),
    (26, _('HHS:RHY – Demonstration Project**')),
    (27, _('VA: Community Contract Emergency Housing')),
    (28, _('VA: Community Contract Residential Treatment Program***')),
    (29, _('VA:Domiciliary Care***')),
    (30, _('VA:Community Contract Safe Haven Program***')),
    (31, _('VA:Grant and Per Diem Program')),
    (32, _('VA:Compensated Work Therapy Transitional Residence***')),
    (33, _('VA:Supportive Services for Veteran Families')),
    (34, _('N/A')),
)


CLIENT_NAME_DATA_QUALITY = {
    1: _('Full name reported'),
    2: _('Partial, street name, or code name reported'),
    8: _('Client doesn’t know'),
    9: _('Client refused'),
    99: _('Data not collected'),
}
CLIENT_NAME_DATA_QUALITY_CHOICES = CLIENT_NAME_DATA_QUALITY.items()


CLIENT_SSN_DATA_QUALITY = {
    1: _('Full SSN reported'),
    2: _('Approximate or partial SSN reported'),
    8: _('Client doesn’t know'),
    9: _('Client refused'),
    99: _('Data not collected'),
}
CLIENT_SSN_DATA_QUALITY_CHOICES = CLIENT_SSN_DATA_QUALITY.items()


CLIENT_DOB_DATA_QUALITY = {
    1: _('Full DOB reported'),
    2: _('Approximate or partial DOB reported'),
    8: _('Client doesn’t know'),
    9: _('Client refused'),
    99: _('Data not collected'),
}
CLIENT_DOB_DATA_QUALITY_CHOICES = CLIENT_DOB_DATA_QUALITY.items()


NC = 99


class Organization (models.Model):
    name = models.TextField()
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)


class ContinuumOfCare (models.Model):
    code = models.CharField(max_length=100)


class Funder (models.Model):
    name = models.TextField()
    program = models.PositiveIntegerField(choices=FUNDING_PROGRAM_CHOICES)


class Project (models.Model):
    # TODO: HOW MUCH DO WE NEED TO BUILD OUT THE PROJECT MODEL? With the finite
    #       number of projects that we have, we can enter their meta-data into
    #       the new system whenever we get it. For now, we just need project
    #       names and administrators (and maybe types, in case it affects what
    #       client information to collect). Also, most users are only going to
    #       be entering information for a single project.

    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    # === All Projects ===
    name = models.TextField()
    organization = models.ForeignKey('Organization')
    coc = models.ManyToManyField('ContinuumOfCare', blank=True)
    type = models.PositiveIntegerField(choices=PROJECT_TYPE_CHOICES)
    #
    # TODO: REVISIT THIS
    #
    # If type is 6 (Services Only), then there's a possibility that this project
    # is affiliated with some other projects. If the project is affiliated, then
    # the affiliated projects must be specified. NOTE: is there a good way to
    # represent this in the admin?
    is_affiliated = models.PositiveIntegerField(choices=YES_NO,
        help_text=_("Is the project affiliated with a residential project?"))
    affiliated_projects = models.ManyToManyField('Project', blank=True)

    # === Emergency Shelters (type 1) ===
    tracking_method = models.PositiveIntegerField(
        choices=PROJECT_TRACKING_METHOD_CHOICES)

    # TODO: CAN WE HAVE MULTIPLE FUNDERS FOR A PROJECT?
    funders = models.ManyToManyField('Funder', blank=True)

    # TODO: Skipped 2.7 (Bed and Unit Inventory)


class Client (models.Model):
    # Collected at record creation

    # == Name ==
    first = models.CharField(max_length=100, blank=True)
    middle = models.CharField(max_length=100, blank=True)
    last = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=100, blank=True)
    name_data_quality = models.PositiveIntegerField(_('Data quality'), choices=CLIENT_NAME_DATA_QUALITY_CHOICES, default=NC)

    def name_display(self):
        name_pieces = []
        if self.first: name_pieces.append(self.first)
        if self.middle: name_pieces.append(self.middle)
        if self.last: name_pieces.append(self.last)
        if self.suffix: name_pieces.append(self.suffix)

        if self.name_data_quality == 1:
            return ' '.join(name_pieces)
        elif self.name_data_quality == 2:
            return '~' + ' '.join(name_pieces)
        else:
            return CLIENT_NAME_DATA_QUALITY[self.name_data_quality]
    name_display.short_description = _('Name')

    # == Social Security Number ==
    ssn = models.CharField(max_length=9, blank=True)
    ssn_data_quality = models.PositiveIntegerField(_('Data quality'), choices=CLIENT_SSN_DATA_QUALITY_CHOICES, default=NC)

    def ssn_display(self):
        # TODO: When should we show a full SSN?
        if self.ssn_data_quality in (1, 2):
            return '***-**-' + self.ssn[-4:]
        else:
            return CLIENT_SSN_DATA_QUALITY[self.ssn_data_quality]
    ssn_display.short_description = _('Social Security')

    # == Date of Birth ==
    dob = models.DateField(_('Date of birth'), blank=True)
    dob_data_quality = models.PositiveIntegerField(_('Data quality'), choices=CLIENT_DOB_DATA_QUALITY_CHOICES, default=NC)

    def dob_display(self):
        if self.dob_data_quality == 1:
            return str(self.dob)
        elif self.dob_data_quality == 2:
            return '~' + str(self.dob)
        else:
            return CLIENT_DOB_DATA_QUALITY[self.dob_data_quality]
    dob_display.short_description = _('Date of birth')

    # == Other fields ==
    gender = models.CharField(max_length=20, blank=True)
    ethnicity = models.CharField(max_length=100, blank=True)
    race = models.CharField(max_length=100, blank=True)
    veteran_status = models.BooleanField()

    def __str__(self):
        return '{} (SSN: {})'.format(self.name_display(), self.ssn_display())

    # Collected at project entry
    # disabling_condition


class Enrollment (models.Model):
    project = models.ForeignKey('Project')
    client = models.ForeignKey('Client')
    start_date = models.DateField()
    end_date = models.DateField()
    exit_destination = models.CharField(max_length=100)
