from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra):
        """Create, save and return new user"""
        if not email:
            raise ValueError('Valid e-mail must be provided!')
        user = self.model(email=self.normalize_email(email), **extra)
        user.username
        user.set_password(password)
        user.save(using=self._db)  # Support multiple DB

        return user

    def create_superuser(self, email, password, first_name, last_name):
        """Create and return superuser"""
        user = self.create_user(email, password, **{"first_name": first_name, "last_name": last_name})
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Organization(models.Model):
    name = models.CharField(max_length=128)
    contact_email = models.EmailField(blank=True)


class User(AbstractBaseUser, PermissionsMixin):

    LANGUAGE_CHOICES = (
        ('hr', 'Hrvatski'),
        ('en', 'English')
    )

    username = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=127, blank=True)
    last_name = models.CharField(max_length=127, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)
    language_preference = models.CharField(choices=LANGUAGE_CHOICES, max_length=8, default='hr')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_admin(self):
        return self.groups.exists() and self.groups.first().name == 'Admin'

    @property
    def is_editor(self):
        return self.groups.exists() and self.groups.first().name == 'Editor'

    @property
    def is_viewer(self):
        return self.groups.exists() and self.groups.first().name == 'Viewer'

    @property
    def app_role_name(self):
        return self.groups.first().name if self.groups.exists() else ''

    @property
    def app_role_id(self):
        return self.groups.first().id if self.groups.exists() else None


class PasswordResetRequest(models.Model):
    received_on = models.DateTimeField(auto_now_add=True)
    uid = models.UUIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    confirmed_on = models.DateTimeField(null=True)

    def __str__(self):
        return self.received_on.isoformat()
