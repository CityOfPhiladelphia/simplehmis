# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0005_add_hud_race_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='project',
            field=models.ForeignKey(to='simplehmis.Project', null=True),
        ),
    ]
