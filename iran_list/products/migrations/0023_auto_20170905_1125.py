# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-05 11:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import iran_list.products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_auto_20170905_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(iran_list.products.models.get_sentinel_user), related_name='added_investments', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
