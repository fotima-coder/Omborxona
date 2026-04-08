

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    branch = models.ForeignKey('main.Branch', on_delete=models.SET_NULL, blank=True, null=True)