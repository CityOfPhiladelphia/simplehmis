# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def copy_assessment_dates(apps, schema_editor):
    HouseholdMember = apps.get_model('simplehmis', 'HouseholdMember')
    for member in HouseholdMember.objects.all():
        try: member.entry_date = member.entry_assessment.project_entry_date
        except: pass
        try: member.exit_date = member.exit_assessment.project_exit_date
        except: pass
        member.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0006_auto_make_project_model_not_blankable'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdmember',
            name='entry_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='householdmember',
            name='exit_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.RunPython(
            copy_assessment_dates,
            noop
        ),
    ]
