from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
class Guest(models.Model):
    Username = models.CharField(max_length=255, unique=True)
    class Meta:
        app_label = 'backend_django'
        db_table = 'Guest'
        
        
class RegisteredUsers(models.Model):
    Username = models.CharField(max_length=255, unique=True)
    Password = models.CharField(max_length=255)
    GamesWon = models.IntegerField(default=0)
    GameDraw = models.IntegerField(default=0)
    GamesLost = models.IntegerField(default=0)
    EloReallyBadChess = models.IntegerField(default=1000)
    EloSecondChess = models.IntegerField(default=1000)
    
    
    def __str__(self):
        return self.Username