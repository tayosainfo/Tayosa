# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='location_latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='location_longitude',
            field=models.FloatField(default=0),
        ),
    ]
