# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-18 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_siteinfo_sub_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='is_acquired',
            field=models.BooleanField(default=False, verbose_name='Is Acquired'),
        ),
        migrations.AlterField(
            model_name='siteinfo',
            name='sub_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Subtitle'),
        ),
    ]
