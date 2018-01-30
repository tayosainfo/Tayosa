# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('mobile_phone_number', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=40)),
                ('pin_number', models.CharField(max_length=10)),
                ('location_latitude', models.IntegerField()),
                ('location_longitude', models.IntegerField()),
                ('is_staff', models.BooleanField(default=False, help_text=b'Designates whether the user can log into the super admin site.', verbose_name=b'staff status')),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name=b'active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name=b'date joined', db_column=b'created_at')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='Farmer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'farmer',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.IntegerField(choices=[(1, b'Kilogram (kg)'), (2, b'Litre (L)')])),
            ],
            options={
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'product_type',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'supplier',
            },
        ),
        migrations.CreateModel(
            name='SupplierProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price_per_unit', models.FloatField(default=0)),
                ('quantity', models.FloatField(default=0)),
                ('product', models.ForeignKey(to='core.Product')),
                ('supplier', models.ForeignKey(to='core.Supplier')),
            ],
            options={
                'db_table': 'supplier_product',
            },
        ),
        migrations.CreateModel(
            name='SupplierService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.ForeignKey(to='core.Service')),
                ('supplier', models.ForeignKey(to='core.Supplier')),
            ],
            options={
                'db_table': 'supplier_service',
            },
        ),
        migrations.CreateModel(
            name='USSDRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=100)),
                ('user_type', models.IntegerField(default=1, choices=[(1, b'Farmer'), (2, b'Supplier')])),
                ('order_type', models.IntegerField(default=1, choices=[(1, b'Product'), (2, b'Service')])),
                ('quantity', models.FloatField(null=True)),
                ('price', models.FloatField(null=True)),
                ('request_closed', models.BooleanField(default=False)),
                ('last_step', models.IntegerField(default=0)),
                ('product', models.ForeignKey(to='core.Product', null=True)),
                ('product_type', models.ForeignKey(to='core.ProductType', null=True)),
                ('service', models.ForeignKey(to='core.Service', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'ussd_request',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(to='core.ProductType'),
        ),
    ]
