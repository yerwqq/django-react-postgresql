from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fio = models.CharField(max_length=256, verbose_name='ФИО', blank=False)
    email = models.EmailField(blank=False, unique=True, verbose_name='Почта')
    phone = models.CharField(max_length=15, verbose_name='Телефон', blank=True)

    def save(self, *args, **kwargs):
        if self.phone and not str(self.phone).startswith('+'):
            self.phone = '+' + self.phone
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.fio} - {self.user.username}'
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'