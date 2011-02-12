from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Track(models.Model):
    title = models.CharField(max_length="200")
    user = models.ForeignKey(User,
        related_name = "tracks",
        blank = True,
        null = True
    )
