from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class Invitem(models.Model):
    """UserManager 를 objects 필드에 사용"""

    id = models.BigIntegerField(unique=True, primary_key=True)
    code = models.CharField(max_length=20, primary_key=True)
    company = models.CharField(max_length=100)
