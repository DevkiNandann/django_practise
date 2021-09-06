from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(blank=True, null=True, max_length=255)
    email = models.EmailField(
        max_length=255, blank=True, null=True, unique=True, db_index=True
    )
    password = models.CharField(blank=True, null=True, max_length=255)
    phone_number = models.CharField(max_length=255, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email"]
