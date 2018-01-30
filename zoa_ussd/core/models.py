from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin
)
from django.utils import timezone
from django.contrib.gis.db import models 
from django.contrib.gis.geos import Point, GEOSGeometry

class UserManager(BaseUserManager):
    """ Custom manager for Member."""

    def _create_user(self, mobile_phone_number, password,
                     is_staff, is_superuser, **extra_fields):
        """ Create and save an Member with the given mobile_phone_number and password.
        :param str mobile_phone_number: user mobile_phone_number
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return custom_user.models.Member user: user
        :raise ValueError: mobile_phone_number is not set
        """
        now = timezone.now()
        if not mobile_phone_number:
            raise ValueError('The given mobile_phone_number must be set')
        is_active = extra_fields.pop("is_active", True)

        user = self.model(
            mobile_phone_number=mobile_phone_number, 
            is_staff=is_staff, 
            is_active=is_active,
            is_superuser=is_superuser, 
            last_login=now,
            date_joined=now, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile_phone_number, password=None, **extra_fields):
        """ Create and save an Member with the given mobile_phone_number and password.
        :param str mobile_phone_number: user mobile_phone_number
        :param str password: user password
        :return custom_user.models.Member user: regular user
        """
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(mobile_phone_number, password, is_staff, False,
                                 **extra_fields)

    def create_superuser(self, mobile_phone_number, password, **extra_fields):
        """ Create and save an Member with the given mobile_phone_number and password.
        :param str mobile_phone_number: user mobile_phone_number
        :param str password: user password
        :return custom_user.models.Member user: admin user
        """
        return self._create_user(mobile_phone_number, password, True, True,
                                 **extra_fields)

    def get_by_natural_key(self, mobile_phone_number):
        return self.get(mobile_phone_number=mobile_phone_number)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=40)
    mobile_phone_number = models.CharField(max_length=20, unique=True)
    pin_number = models.CharField(max_length=10)

    is_staff = models.BooleanField(('staff status'), default=False, help_text=(
            'Designates whether the user can log into the super admin site.'))
    is_active = models.BooleanField(('active'), default=True, help_text=(
        'Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'))
    
    date_joined = models.DateTimeField(('date joined'), 
        auto_now_add=True, db_column="created_at")

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'mobile_phone_number'

    objects = UserManager()

    class Meta:
        db_table = "user"

    def __unicode__(self):
        return self.name or self.mobile_phone_number

    def get_short_name(self):
        return self.__unicode__()

class Supplier(models.Model):
    user = models.ForeignKey('User')

    geom = models.PointField(srid=4326, null=True)
    objects = models.GeoManager()

    class Meta:
        db_table = "supplier"

    def __unicode__(self):
        return self.user.name

class ProductType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "product_type"

    def __unicode__(self):
        return self.name

class Product(models.Model):
    UNITS = (
        (1, 'kg'),
        (2, 'L'),
    )
    name = models.CharField(max_length=50)
    product_type = models.ForeignKey('ProductType')
    unit = models.IntegerField(choices=UNITS)

    class Meta:
        db_table = "product"

    def __unicode__(self):
        return self.name

class SupplierProduct(models.Model):
    supplier = models.ForeignKey('Supplier', related_name="supplier_products")
    product  = models.ForeignKey('Product', related_name="product_suppliers")

    price_per_unit = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    class Meta:
        db_table = "supplier_product"

    def __unicode__(self):
        return self.product.name

class Service(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = "service"

    def __unicode__(self):
        return self.name

class SupplierService(models.Model):
    supplier = models.ForeignKey('Supplier', related_name="supplier_services")
    service = models.ForeignKey('Service', related_name="service_suppliers")

    class Meta:
        db_table = "supplier_service"

    def __unicode__(self):
        return self.service.name

class Farmer(models.Model):
    user = models.OneToOneField('User', related_name="farmer_profile")

    geom = models.PointField(srid=4326, null=True)
    objects = models.GeoManager()
    
    class Meta:
        db_table = "farmer"

    def __unicode__(self):
        return self.user.name

class USSDRequest(models.Model):
    FARMER_USER = 1
    SUPPLIER_USER = 2
    USER_TYPES = (
        (1, "Farmer"),
        (2, "Supplier"),
    )

    PRODUCT_ORDER = 1
    SERVICE_ORDER = 2
    
    ORDER_TYPES = (
        (1, "Product"),
        (2, "Service"),
    )

    MENU_FIRST = 0
    MENU_USER_TYPE = 1
    MENU_SERVICE = 2
    MENU_PRODUCT_SERVICE_CATEGORY = 3
    MENU_PRODUCT = 4
    MENU_QUANTITY = 5
    MENU_PRICE = 6
    MENU_LAST = 7
    
    MENUS = (
        (MENU_FIRST, "First Item"),
        (MENU_USER_TYPE, "User Type Selection"),
        (MENU_SERVICE, "Service Type Selection"),
        (MENU_PRODUCT_SERVICE_CATEGORY, "Service/Product Category Selection"),
        (MENU_PRODUCT, "Product Selection"),
        (MENU_QUANTITY, "Quantity Entry"),
        (MENU_PRICE, "Price Entry"),
        (MENU_LAST, "Last Item"),
    )

    session_id = models.CharField(max_length=100)

    user = models.ForeignKey('User', null=True)
    user_type = models.IntegerField(default=FARMER_USER, choices=USER_TYPES)
    
    order_type = models.IntegerField(default=PRODUCT_ORDER, choices=ORDER_TYPES)
    service = models.ForeignKey('Service', null=True)
    
    product_type = models.ForeignKey('ProductType', null=True)
    product = models.ForeignKey('Product', null=True)
    quantity = models.FloatField(null=True)
    price = models.FloatField(null=True)

    request_closed = models.BooleanField(default=False)

    last_step = models.IntegerField(default=MENU_FIRST, choices=MENUS)

    class Meta:
        db_table = "ussd_request"
        unique_together = ('session_id', 'user')

    