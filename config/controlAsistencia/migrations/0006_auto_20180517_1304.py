# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-17 13:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('controlAsistencia', '0005_auto_20180515_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='absence',
            name='origin',
            field=models.IntegerField(choices=[(0, 'Llegada tarde'), (1, 'Retiro anticipado')], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='absence',
            name='time',
            field=models.TimeField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='absence',
            name='percentage',
            field=models.FloatField(choices=[(0.25, '1/4'), (0.5, '1/2'), (0.75, '3/4'), (1.0, '1')], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='preceptor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='year',
            name='division',
            field=models.CharField(choices=[('a', 'A'), ('b', 'B'), ('c', 'C')], max_length=1),
        ),
    ]
