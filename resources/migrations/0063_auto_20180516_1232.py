# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-16 12:32
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0062_auto_20180516_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='home',
            name='body_content',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='\n        Body of result block\n    '),
        ),
        migrations.AlterField(
            model_name='home',
            name='footer_content',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='\n        Footer of result block\n    '),
        ),
        migrations.AlterField(
            model_name='home',
            name='result_heading',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='\n        Heading of result block\n    '),
        ),
    ]