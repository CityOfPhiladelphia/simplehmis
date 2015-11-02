# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0008_add_index_on_client_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('name',)},
        ),
    ]
