"""
Accounts models — UserProfile, ViewedProduct
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended profile — one-to-one with Django's built-in User"""
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio        = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class ViewedProduct(models.Model):
    """Records which products a logged-in user has viewed — used for recommender"""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_products')
    product    = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE)
    viewed_at  = models.DateTimeField(auto_now=True)

    class Meta:
        # One record per user-product pair, updated on each view
        unique_together = ['user', 'product']
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.username} viewed {self.product.name}'


# Auto-create a UserProfile whenever a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
