"""
Shop models — CartItem, Order, OrderItem
"""

from django.db import models
from django.contrib.auth.models import User
from catalogue.models import Product


class CartItem(models.Model):
    """A product in a user's active cart — deleted with user"""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.user.username} — {self.product.name} x{self.quantity}'


class Order(models.Model):
    """A completed simulated purchase — kept when user is deleted"""
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
    ]

    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    total       = models.DecimalField(max_digits=10, decimal_places=2)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.user.username if self.user else "Deleted User"}'


class OrderItem(models.Model):
    """A single product line within an Order"""
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity   = models.PositiveIntegerField()
    price      = models.DecimalField(max_digits=8, decimal_places=2)  # Price at time of purchase

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product.name if self.product else "Deleted Product"} x{self.quantity}'