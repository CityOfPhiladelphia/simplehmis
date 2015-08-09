# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientannualassessment',
            name='income_notes',
            field=models.TextField(blank=True, verbose_name='Note all sources and dollar amounts for each source.'),
        ),
        migrations.AddField(
            model_name='clientannualassessment',
            name='income_status',
            field=models.PositiveIntegerField(default=None, choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (None, '(Please choose an option)')], null=True, verbose_name='Income from any source?'),
        ),
        migrations.AddField(
            model_name='cliententryassessment',
            name='income_notes',
            field=models.TextField(blank=True, verbose_name='Note all sources and dollar amounts for each source.'),
        ),
        migrations.AddField(
            model_name='cliententryassessment',
            name='income_status',
            field=models.PositiveIntegerField(default=None, choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (None, '(Please choose an option)')], null=True, verbose_name='Income from any source?'),
        ),
        migrations.AddField(
            model_name='clientexitassessment',
            name='income_notes',
            field=models.TextField(blank=True, verbose_name='Note all sources and dollar amounts for each source.'),
        ),
        migrations.AddField(
            model_name='clientexitassessment',
            name='income_status',
            field=models.PositiveIntegerField(default=None, choices=[(0, 'No'), (1, 'Yes'), (8, 'Client doesn’t know'), (9, 'Client refused'), (None, '(Please choose an option)')], null=True, verbose_name='Income from any source?'),
        ),
    ]
