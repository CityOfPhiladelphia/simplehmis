# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0007_add_enrollment_and_exit_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='first',
            field=models.CharField(verbose_name='First name', blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='last',
            field=models.CharField(verbose_name='Last name', blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='middle',
            field=models.CharField(verbose_name='Middle name', blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='ssn',
            field=models.CharField(verbose_name='SSN', help_text='Enter 9 digit SSN Do not enter hyphens EX: 555210987', db_index=True, blank=True, max_length=9),
        ),
        migrations.AlterField(
            model_name='clientexitassessment',
            name='project_exit_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='present_at_enrollment',
            field=models.BooleanField(verbose_name='Present?', default=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.TextField(db_index=True),
        ),
    ]
