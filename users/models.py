from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email must be set')
        if not first_name:
            raise ValueError('First name must be set')
        if not last_name:
            raise ValueError('Last name must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.is_superuser = True
        user.is_active = True 

        user.save(using=self._db)
        return user


# Custom User Model that is used in the project instead of the Django default User
class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150,)
    last_name = models.CharField(max_length=150)

    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Address')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    zip_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Zip Code')

    is_active = models.BooleanField(default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'Users'
        ordering = ['email']

    # Assigns this model to the custom manager
    objects = CustomUserManager() 

    # The field used as the unique identifier for login
    USERNAME_FIELD = 'email'

    # Fields required when creating a user via 'createsuperuser' command
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    # Returns the first_name plus the last_name, with a space in between.
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # Returns the short name for the user (first name + last name + dot)
    def get_short_name(self):
        return f"{self.first_name} {self.last_name[0]}.".strip()
