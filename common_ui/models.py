from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """User 에서 사용하기 위한 UserManager 생성"""
    def create_user(self, email, password=None, **extra_fields):
        """일반 유저로 생성할 경우"""
        if not email:
            raise ValueError('이메일을 입력해주세요')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user.is_active = True

        return user

    def create_superuser(self, email, password):
        """superuser 로 user 를 생성할 경우 필드값을 True 로 변경"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """UserManager 를 objects 필드에 사용"""
    id = models.BigIntegerField(unique=True)
    email = models.EmailField(max_length=255, unique=True)
    user_name = models.CharField(max_length=255)
    passwd = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    alias = models.CharField(max_length=20, null=True)
    profile_img = models.ImageField(upload_to='profile', null=True)
    cover_img = models.ImageField(upload_to='cover', null=True)
    introduce = models.TextField(max_length=255)

    # UserManager 을 재정의하여 사용
    objects = UserManager()
    # USERNAME 를 email 로 사용
    USERNAME_FIELD = 'email'