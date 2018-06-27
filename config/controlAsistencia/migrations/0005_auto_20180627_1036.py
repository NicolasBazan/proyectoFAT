# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-06-27 13:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controlAsistencia', '0004_auto_20180627_1025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='absence',
            name='datetime',
        ),
        migrations.AddField(
            model_name='absence',
            name='date',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='absence',
            name='time',
            field=models.TimeField(default=None),
            preserve_default=False,
        ),
    ]
