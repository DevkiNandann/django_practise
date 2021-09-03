from django.db import models


class User(models.Model):
    user_id = models.CharField(blank=True, null=True, max_length=255)
    email = models.EmailField(
        max_length=255, blank=True, null=True, unique=True, db_index=True
    )
    phone_number = models.CharField(max_length=255, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(blank=True, null=True)
