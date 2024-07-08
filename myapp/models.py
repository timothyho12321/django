from django.db import models

# Create your models here.

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    age = models.CharField(max_length=100, default='0')
    
    
class SearchResults(models.Model):
    url = models.URLField(max_length=2048)  # Increase the max_length to accommodate longer URLs
    description = models.TextField()