"""
Catalogue models — Category, Subcategory, Product, Review, WishlistItem
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    """Top-level product category e.g. Clothing, Accessories"""
    name        = models.CharField(max_length=80)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Second-level category e.g. T-Shirts under Clothing"""
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name        = models.CharField(max_length=80)
    slug        = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'subcategories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.category.name} → {self.name}'


class Product(models.Model):
    """A single sellable product in the Bloom shop"""
    name          = models.CharField(max_length=120)
    slug          = models.SlugField(unique=True)
    description   = models.TextField(max_length=1000)
    price         = models.DecimalField(max_digits=8, decimal_places=2)
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    subcategory   = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image         = models.ImageField(upload_to='products/', blank=True, null=True)
    stock         = models.PositiveIntegerField(default=0)
    tags          = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    trees_per_unit = models.PositiveIntegerField(default=0, help_text='Trees planted per unit sold')
    created_at    = models.DateTimeField(auto_now_add=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def avg_rating(self):
        """Return average star rating or None if no reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(r.stars for r in reviews) / len(reviews), 1)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Star rating and optional text review — logged-in users only"""
    STARS = [(i, str(i)) for i in range(1, 6)]

    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    stars      = models.IntegerField(choices=STARS)
    text       = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One review per user per product
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.product.name} ({self.stars}★)'


class WishlistItem(models.Model):
    """Saved product for a logged-in user"""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} → {self.product.name}'
