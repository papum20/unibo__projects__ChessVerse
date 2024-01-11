from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission


class Guest(models.Model):
    Username = models.CharField(max_length=255, unique=True)

    class Meta:
        app_label = "backend"
        db_table = "Guest"


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)


class RegisteredUsers(AbstractUser):
    EloReallyBadChess = models.IntegerField(default=400)
    session_id = models.CharField(max_length=255, default="")
    GamesWon = models.IntegerField(default=0)
    GamesLost = models.IntegerField(default=0)
    GamesDrawn = models.IntegerField(default=0)
    score_ranked = models.IntegerField(default=0)

    groups = models.ManyToManyField(Group, blank=True, related_name="registered_users")
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name="registered_users"
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Games(models.Model):
    username1 = models.CharField(max_length=255)
    username2 = models.CharField(max_length=255)
    png = models.CharField(max_length=255)

    class Meta:
        app_label = "backend"
        db_table = "Games"


class DailyLeaderboard(models.Model):
    username = models.CharField(max_length=255)
    moves_count = models.PositiveIntegerField()
    challenge_date = models.CharField(max_length=8, default="01011970")
    result = models.CharField(max_length=10)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["moves_count"]


class WeeklyLeaderboard(models.Model):
    username = models.CharField(max_length=255)
    moves_count = models.PositiveIntegerField()
    challenge_date = models.CharField(max_length=6, default="511970")
    result = models.CharField(max_length=10)

    class Meta:
        ordering = ["moves_count"]
