from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.models import User


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # use auto_now_add for created timestamp

    def __str__(self):
        return f"{self.user.username},{self.subject}"

    class Meta:
        ordering = ['-created_at']

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = CKEditor5Field('Content', config_name='default')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    STATUS = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    status = models.CharField(max_length=7, choices=STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
