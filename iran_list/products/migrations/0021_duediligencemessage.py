# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-04 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_investment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DueDiligenceMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'New'), ('on_hand', 'On hand'), ('closed', 'Closed')], default='new', max_length=10, verbose_name='Status')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('company_description', models.TextField(verbose_name='Company Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Due Diligence Message',
                'verbose_name_plural': 'Due Diligence Messages',
            },
        ),
    ]
