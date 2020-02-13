from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from auxqueue import settings

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    access_token = models.CharField(max_length=300, blank=True, null=True)
    refresh_token = models.CharField(max_length=300, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Friendship(models.Model):
    user_one = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_one', on_delete=models.CASCADE)
    user_two = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_two', on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0)
    action_user_id = models.SmallIntegerField(default=0)
    permissions = models.CharField(max_length=300, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_one', 'user_two',)

