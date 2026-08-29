from django.db import models
from django.conf import settings

class Story(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=250)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100)
