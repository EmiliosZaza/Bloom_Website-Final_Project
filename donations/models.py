"""
Donations models — Donation
"""

from django.db import models
from django.contrib.auth.models import User

TREES_PER_DOLLAR = 5  # $1 = 5 trees


class Donation(models.Model):
    """A monetary donation tied to a logged-in user"""
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount           = models.DecimalField(max_digits=8, decimal_places=2)
    trees_equivalent = models.PositiveIntegerField(editable=False)
    message          = models.TextField(max_length=300, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-calculate trees from amount at $1 = 5 trees
        self.trees_equivalent = int(self.amount * TREES_PER_DOLLAR)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} donated ${self.amount} ({self.trees_equivalent} trees)'
