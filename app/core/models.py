"""
Database models.
"""
from django.db import models
from django.conf import settings
from django.utils.dateparse import parse_datetime

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
import os
import uuid

def ml_model_upload_path(instance, filename):
    """Generate file path for new model"""
    ext= os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads','mlmodels',filename)

class UserManager(BaseUserManager):
    """Manager pour les users"""
    def create_user(self, email, password=None, **extra_fields):
        """Create , save and return a new user"""
        if not email:
            raise ValueError('User il doit avoir une adresse email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system. """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Appariel(models.Model):
    """Appariel model."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    user= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='appariels', on_delete=models.CASCADE)


    class Meta():
         ordering = ('name',)
    def __str__(self):
        return self.name


class AppData(models.Model):
     appariel= models.ForeignKey(Appariel, on_delete=models.CASCADE)
     datetime = models.DateTimeField()
     data = models.JSONField()

     class Meta :
          db_table= "core_appariel_data"
          unique_together = ('appariel','datetime')

class MLModel(models.Model):
    """MLModel model."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    appariel = models.ForeignKey(Appariel, on_delete=models.CASCADE)
    model_file = models.FileField(upload_to=ml_model_upload_path)


    class Meta():
        ordering = ('name',)

    def __str__(self):
        return self.name


