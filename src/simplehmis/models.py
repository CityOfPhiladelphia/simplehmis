# -*- encoding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.utils.translation import ugettext as _
from simplehmis import consts

import logging
logger = logging.getLogger(__name__)


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
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    name = models.TextField()

    objects = ProjectManager()

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def __str__(self):
        return self.name


class Client (TimestampedModel):
    first = models.CharField(max_length=100, blank=True)
    middle = models.CharField(max_length=100, blank=True)
    last = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=100, blank=True)
    dob = models.DateField(_('Date of birth'), blank=True)
    ssn = models.CharField(max_length=9, blank=True,
        help_text=_('Enter 9 digit SSN Do not enter hyphens EX: 555210987'))
    gender = models.PositiveIntegerField(blank=True, choices=consts.HUD_CLIENT_GENDER.items())
    other_gender = models.TextField(blank=True,
        help_text=_('If "Other" for gender, please specify.'))
    ethnicity = models.PositiveIntegerField(blank=True, null=True, choices=consts.HUD_CLIENT_ETHNICITY.items())
    race = models.PositiveIntegerField(blank=True, null=True, choices=consts.HUD_CLIENT_RACE.items())
    # TODO: veteran status field should not validate if it conflicts with the
    #       client's age.
    veteran_status = models.PositiveIntegerField(blank=True, null=True, choices=consts.HUD_YES_NO.items(),
        help_text=_('Only collect this field if client is over 18.'))

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

    @staticmethod
    def autocomplete_search_fields():
        return ("first__icontains", "last__icontains", "middle__icontains", "ssn__icontains")

    def __str__(self):
        return '{} (SSN: {})'.format(self.name_display(), self.ssn_display())


class Enrollment (TimestampedModel):
    """
    A household enrollment
    """
    project = models.ForeignKey('Project')
    # hoh = models.OneToOne('ClientEnrollment', verbose_name='Head of household')
    # dependents = models.ManyToManyField('ClientEnrollment')

    def hoh(self):
        return self.members.all()[0]


class ClientEnrollment (TimestampedModel):
    client = models.ForeignKey('Client')
    hoh_relationship = models.PositiveIntegerField(_('Relationship to Head of Household'), choices=consts.HUD_CLIENT_HOH_RELATIONSHIP.items())
    substance_abuse_issues = models.PositiveIntegerField(choices=consts.HUD_YES_NO.items(), blank=True, null=True,
        help_text=_('If Yes, please enter detail information in Substance Abuse Detail field'))
    substance_abuse_detail = models.TextField(blank=True)
    mental_health_issues = models.PositiveIntegerField(choices=consts.HUD_YES_NO.items(), blank=True, null=True,
        help_text=_('If Yes, please enter detail information in Mental Health Detail field'))
    mental_health_detail = models.TextField(blank=True)
    medical_issues = models.PositiveIntegerField(choices=consts.HUD_YES_NO.items(), blank=True, null=True,
        help_text=_('If Yes, please enter detail information in Medical Detail field'))
    medical_detail = models.TextField(blank=True)

    household = models.ForeignKey('Enrollment', related_name='members')

    enrollment_as_hoh = models.OneToOneField('Enrollment', related_name='hoh', null=True, blank=True)
    enrollment_as_dependant = models.ForeignKey('Enrollment', related_name='dependents', null=True, blank=True)

    def __str__(self):
        return str(self.client)
