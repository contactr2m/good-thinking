# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-16 11:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_auto_20170616_1001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='hero_image_position',
        ),
    ]
