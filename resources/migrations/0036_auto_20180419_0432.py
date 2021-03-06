# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-19 04:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0019_delete_filter'),
        ('resources', '0035_auto_20171107_1143'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeFooterLinksOne',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('footer_link', models.URLField(blank=True)),
                ('footer_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='footer_links_one', to='resources.Main')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HomeFooterLinksTwo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.TextField(blank=True)),
                ('footer_link', models.URLField(blank=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='footer_links_two', to='resources.Main')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='homefooterlinks',
            name='footer_image',
        ),
        migrations.RemoveField(
            model_name='homefooterlinks',
            name='page',
        ),
        migrations.DeleteModel(
            name='HomeFooterLinks',
        ),
    ]
