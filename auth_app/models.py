from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    activation_uid = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
