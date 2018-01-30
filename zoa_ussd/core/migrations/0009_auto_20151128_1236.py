# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20151124_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='short_name',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.IntegerField(choices=[(1, b'kg'), (2, b'L')]),
        ),
        migrations.AlterField(
            model_name='supplierservice',
            name='service',
            field=models.ForeignKey(related_name='service_suppliers', to='core.Service'),
        ),
        migrations.AlterField(
            model_name='supplierservice',
            name='supplier',
            field=models.ForeignKey(related_name='supplier_services', to='core.Supplier'),
        ),
    ]
