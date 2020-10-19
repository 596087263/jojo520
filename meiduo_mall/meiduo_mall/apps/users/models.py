# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):

    mobile=models.CharField(max_length=11,unique=True,verbose_name='手机号')
    class Mate:
        db_table='tb_users'
        verbose_name='用户'
        verbose_name_plural=verbose_name
        def __str__(self):
            return self.username

