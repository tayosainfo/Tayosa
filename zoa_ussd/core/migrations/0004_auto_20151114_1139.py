# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151021_0945'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='location_latitude',
        ),
        migrations.RemoveField(
            model_name='user',
            name='location_longitude',
        ),
        migrations.AlterField(
            model_name='ussdrequest',
            name='last_step',
            field=models.IntegerField(default=0, choices=[(0, b'First Item'), (1, b'User Type Selection'), (2, b'Service Type Selection'), (3, b'Service/Product Category Selection'), (4, b'Product Selection'), (5, b'Quantity Entry'), (6, b'Price Entry'), (7, b'Last Item')]),
        ),
        migrations.AlterField(
            model_name='ussdrequest',
            name='session_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='ussdrequest',
            unique_together=set([('session_id', 'user')]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
