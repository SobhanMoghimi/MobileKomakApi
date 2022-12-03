from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

# Create your models here.


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, email, name, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """Create and save a new superuser with given details"""
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """User profile model for the system Database"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    object = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """Retrieve full name of user"""
        return self.name

    def get_short_name(self):
        """Retrieve short name of user"""
        return self.name

    def __str__(self):
        """Return string representation of our user"""
        return self.email


class excel_data(models.Model):
    """Model for excel data"""
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=255)
    order_price = models.FloatField()
    stop_loss = models.FloatField()
    take_profit = models.FloatField()
    contract_type = models.CharField(max_length=10)
    signal = models.BooleanField()
    total_position = models.FloatField()
    initial_margin = models.FloatField()
    total_deposit = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    token_quantity = models.FloatField(default=0)
    leverage = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)


class ConstantDatas(models.Model):
    """Model for constant data"""
    id = models.AutoField(primary_key=True)
    signal = models.BooleanField()
    total_position = models.FloatField()
    initial_margin = models.FloatField()
    total_deposit = models.FloatField()

    def __str__(self):
        return str(self.id)