# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-06 14:52
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20170602_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='banner',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='Banner at the top of every page'),
        ),
    ]
