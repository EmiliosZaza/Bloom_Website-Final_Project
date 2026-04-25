"""
Core views — home, impact, about, contact
Tree totals come from purchases + donations only.
"""

from django.shortcuts import render
from .models import ActivityEvent
from donations.models import Donation
from shop.models import Order, OrderItem


def get_total_trees():
    purchase_trees = sum(
        int(item.price * item.quantity * 5)
        for item in OrderItem.objects.select_related('product').all()
    )
    donation_trees = sum(d.trees_equivalent for d in Donation.objects.all())
    return purchase_trees + donation_trees


def home(request):
    total_trees     = get_total_trees()
    total_orders    = Order.objects.count()
    total_donations = Donation.objects.count()
    feed            = ActivityEvent.objects.all().order_by('-created_at')[:8]

    return render(request, 'core/index.html', {
        'total_trees':     total_trees,
        'total_orders':    total_orders,
        'total_donations': total_donations,
        'feed':            feed,
    })


def impact(request):
    total_trees = get_total_trees()
    return render(request, 'core/impact.html', {'total_trees': total_trees})


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')