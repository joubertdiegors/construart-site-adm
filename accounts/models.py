from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField("Telefone", max_length=20, blank=True)
    is_manager = models.BooleanField("É gestor?", default=False)

    def __str__(self):
        return self.username