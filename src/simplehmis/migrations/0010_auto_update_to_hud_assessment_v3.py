# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from dateutil.relativedelta import relativedelta


def map_assessment(assessment):
    """
    *If*
    Version 2.1 – 3.9   “Residence prior to project entry”      Response 1 (ES); Response 16 (streets); or Response 18 (SH) = yes
    *OR the following is true*
    Version 2.1 – 3.17.1    “Continuously homeless for at least one year”   Response 1 = Yes

    *Then set*
    Version 3.0 – 3.17.1    “Client entering from the streets, ES, or SH”   to  Response 1 = Yes
    *Or else set*
    Version 3.0 – 3.17.1    “Client entering from the streets, ES, or SH”   to  Response 0 = No

    NOTE: I modified this a bit. If the data quality on 2.1 – 3.9 and
    2.1 – 3.17.1 are both low, I set the data quality of 3.0 – 3.17.1 to the
    highest data quality between them.

    If the field 1 calculations above = a response of yes to “Client entering
    for the streets, ES or SH” then  calculate the approximate date by
    subtracting the response from the retired field “Total Number of months
    continually homeless immediately prior to project entry” (3.17.2.A) from the
    project entry month (3.10).  [e.g., an entry date of 6/15/2015 with “3”
    months of homelessness prior to entry makes the date 3/15/2015.]

    ----------

    Dependent B to Field 2: Total number of months homeless on the street, in
    ES, or SH in the past three years

    Directly map the responses for “Total number of months homeless on the
    streets, in ES, or SH in the past three years” to the “Total Number of
    months homeless in the past three years”. Note that responses of “0” months
    in Version 2.1 must be mapped to “1 month” in Version 3.

    """
    if assessment.prior_residence in (1, 16, 18) or \
       assessment.homeless_at_least_one_year == 1:
        assessment.entering_from_streets = 1  # Yes
    elif assessment.prior_residence in (8, 9, 99) and \
         assessment.homeless_at_least_one_year in (8, 9, 99):
        assessment.entering_from_streets = min(assessment.prior_residence, assessment.homeless_at_least_one_year)
    else:
        assessment.entering_from_streets = 0  # No

    if assessment.entering_from_streets == 1:
        month_count = assessment.homeless_months_prior or 0
        assessment.homeless_start_date = assessment.project_entry_date - relativedelta(months=month_count)

    # ----------

    if assessment.homeless_months_in_three_years == 100:
        assessment.homeless_months_in_three_years = 101
    elif assessment.homeless_months_in_three_years == 7:
        assessment.homeless_months_in_three_years = 113

    return assessment


def map_to_hud_v3_assessment_fields(apps, schema_editor):
    HouseholdMember = apps.get_model('simplehmis', 'HouseholdMember')
    for member in HouseholdMember.objects.all():
        try:
            assessment = member.entry_assessment
            map_assessment(assessment)
            assessment.save()
        except models.ObjectDoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0009_auto_set_project_model_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliententryassessment',
            name='entering_from_streets',
            field=models.PositiveIntegerField(default=None, choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], null=True, verbose_name='Is the client entering from the streets, shelter or safe haven? (i.e. Did the client sleep in a shelter, safe haven, or on the streets the night before entering the project?)'),
        ),
        migrations.AddField(
            model_name='cliententryassessment',
            name='homeless_start_date',
            field=models.DateField(blank=True, help_text='<ul><li>If client is unsure of the exact day, enter an approximate date.</li><li>If a client moved from one homeless situation to another (i.e. went from the streets to a safe haven, back to the streets, then into shelter, etc), then enter the date the client first became homeless.</li></ul>', null=True, verbose_name='[IF YES] What was the approximate date the client started staying in that homeless situation? (i.e. when was the last time the client had a place to sleep that was not on the street, in an emergency shelter, or safe haven)?'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='homeless_in_three_years',
            field=models.PositiveIntegerField(default=None, choices=[(0, 'Never in 3 years'), (1, 'One time'), (2, 'Two times'), (3, 'Three times'), (4, 'Four or more times'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], null=True, verbose_name='Regardless of where they stayed last night – Number of times the client has been on the streets, in ES, or SH in the past three years including today.'),
        ),
        migrations.AlterField(
            model_name='cliententryassessment',
            name='homeless_months_in_three_years',
            field=models.PositiveIntegerField(blank=True, default=None, choices=[(101, 'One Month'), (102, '2'), (103, '3'), (104, '4'), (105, '5'), (106, '6'), (107, '7'), (108, '8'), (109, '9'), (110, '10'), (111, '11'), (112, '12'), (113, 'More than 12 months'), (8, 'Client doesn’t know'), (9, 'Client refused'), (99, 'Data not collected'), (None, '(Please choose an option)')], null=True, verbose_name='Total number of months homeless (i.e., on the street, in an emergency shelter, or safe haven) in the past three (3) years'),
        ),
        migrations.RunPython(
            map_to_hud_v3_assessment_fields,
        ),
        migrations.RemoveField(
            model_name='cliententryassessment',
            name='homeless_months_prior',
        ),
        migrations.RemoveField(
            model_name='cliententryassessment',
            name='homeless_at_least_one_year',
        ),
    ]
