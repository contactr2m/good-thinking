# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-12 10:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import resources.models.resources


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0023_tip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('resourcepage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.ResourcePage')),
            ],
            options={
                'abstract': False,
            },
            bases=('resources.resourcepage',),
        ),
        migrations.AddField(
            model_name='resourcepage',
            name='latitude',
            field=resources.models.resources.LatitudeField(blank=True, help_text='\n            latitude. This should be a number between -90 and 90\n        ', max_length=255),
        ),
        migrations.AddField(
            model_name='resourcepage',
            name='longitude',
            field=resources.models.resources.LongitudeField(blank=True, help_text='\n            longitude. This should be a number between -180 and 180\n        ', max_length=255),
        ),
    ]
