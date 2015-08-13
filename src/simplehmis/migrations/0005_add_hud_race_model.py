# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def make_race_entries(apps, schema_editor):
    from simplehmis.consts import HUD_CLIENT_RACE
    ClientRace = apps.get_model('simplehmis', 'ClientRace')
    for value, label in HUD_CLIENT_RACE:
        if value is None:
            continue
        ClientRace.objects.create(hud_value=value, label=label)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('simplehmis', '0004_auto_alter_default_hud_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientRace',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('label', models.CharField(max_length=100)),
                ('hud_value', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='client',
            name='race',
        ),
        migrations.AddField(
            model_name='client',
            name='race',
            field=models.ManyToManyField(null=True, verbose_name='Race', blank=True, to='simplehmis.ClientRace', default=None),
        ),
        migrations.RunPython(
            make_race_entries,
            reverse_code=noop
        ),
    ]
