# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-10 10:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_auto_20170910_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='amount',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Investment Amount'),
        ),
    ]
