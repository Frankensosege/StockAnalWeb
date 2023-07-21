from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class Invitem(models.Model):
    """UserManager 를 objects 필드에 사용"""

    user_id = models.BigIntegerField(unique=True)
    code = models.CharField(max_length=20)
    company = models.CharField(max_length=100)
