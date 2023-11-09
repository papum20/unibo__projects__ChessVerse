from django.db import models

class Guest(models.Model):
    Username = models.CharField(max_length=255, unique=True)
    class Meta:
        app_label = 'backend_django'
        db_table = 'Guest'
        
        
