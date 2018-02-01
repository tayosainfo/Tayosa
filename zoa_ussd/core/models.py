from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin
)
from django.utils import timezone

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

    @property
    def pin_number(self):
        return self.password

    @pin_number.setter
    def pin_number(self, _pin_number):
        self.set_password(_pin_number)

    def __unicode__(self):
        return self.name or self.mobile_phone_number

    def get_short_name(self):
        return self.__unicode__()
