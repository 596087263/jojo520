# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):

    mobile=models.CharField(max_length=11,unique=True,verbose_name='手机号')
    identifier = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'identifier'

    class Mate:
        db_table='tb_users'



        # def __str__(self):
        #     return self.username