# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20151114_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='farmer',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True),
        ),
        migrations.AlterField(
            model_name='farmer',
            name='user',
            field=models.OneToOneField(related_name='farmer_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='product',
            field=models.ForeignKey(related_name='product_suppliers', to='core.Product'),
        ),
        migrations.AlterField(
            model_name='supplierproduct',
            name='supplier',
            field=models.ForeignKey(related_name='supplier_products', to='core.Supplier'),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
