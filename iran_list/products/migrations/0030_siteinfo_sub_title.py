# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-11 08:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_auto_20170910_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteinfo',
            name='sub_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Title'),
        ),
    ]