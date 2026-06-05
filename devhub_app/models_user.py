from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model to allow for future flexibility and demonstrate 
    real-world best practices.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
