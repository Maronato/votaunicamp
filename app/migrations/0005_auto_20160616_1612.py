# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-16 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20160616_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='args',
            name='text',
            field=models.CharField(max_length=10001),
        ),
    ]
