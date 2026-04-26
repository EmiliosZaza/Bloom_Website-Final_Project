#Core models — ActivityEvent

from django.db import models
from django.contrib.auth.models import User


class ActivityEvent(models.Model):
    #Site-wide activity log shown on the homepage feed
    TYPE_CHOICES = [
        ('complete', 'Completed'),
        ('add',      'Added'),
        ('update',   'Updated'),
        ('donate',   'Donated'),
        ('purchase', 'Purchased'),
    ]

    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text       = models.CharField(max_length=300)
    tag        = models.CharField(max_length=40)
    label      = models.CharField(max_length=40)
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type}: {self.text[:60]}'