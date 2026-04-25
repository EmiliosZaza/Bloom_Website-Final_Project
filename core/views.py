"""
Core views — home, impact, about, contact
Tree totals come from purchases + donations only.
"""

from django.shortcuts import render
from .models import ActivityEvent
from donations.models import Donation
from shop.models import Order, OrderItem


def get_total_trees():
    """
    Global tree count = (all order item subtotals × 5) + (all donation amounts × 5)
    $1 = 5 trees across both revenue streams.
    """
    purchase_trees = sum(
        int(item.price * item.quantity * 5)
        for item in OrderItem.objects.select_related('product').all()
    )
    donation_trees = sum(d.trees_equivalent for d in Donation.objects.all())
    return purchase_trees + donation_trees


def home(request):
    """Homepage — stats from DB, activity feed."""
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
    """Impact page — live tree count from purchases and donations."""
    total_trees = get_total_trees()
    return render(request, 'core/impact.html', {'total_trees': total_trees})


def about(request):
    """About page — team volunteers passed as context."""
    volunteers = [
        {
            'image':    'assets/volunteer-sarah.png',
            'initials': 'SM',
            'role':     'Site Leader · Athens',
            'name':     'Sarah M.',
            'quote':    'Every oak I plant is a letter to the future. Bloom gave me the tools to write thousands of them.',
            'trees':    847,
            'years':    4,
        },
        {
            'image':    'assets/testimonial-james.jpg',
            'initials': 'JK',
            'role':     'Ecologist · Thessaloniki',
            'name':     'James K.',
            'quote':    'Bloom is the fastest, most tangible conservation work I\'ve ever been part of.',
            'trees':    1240,
            'years':    6,
        },
        {
            'image':    'assets/testimonial-will.jpg',
            'initials': 'WS',
            'role':     'Corporate Partner · Athens',
            'name':     'Will S.',
            'quote':    'We brought 22 colleagues for a corporate day. Every single person left energized.',
            'trees':    560,
            'years':    2,
        },
        {
            'image':    'assets/testimonial-nina.jpg',
            'initials': 'NC',
            'role':     'Nursery Lead · Lefkada',
            'name':     'Nina C.',
            'quote':    'Watching seedlings leave the nursery and become part of a real woodland — there\'s nothing quite like it.',
            'trees':    920,
            'years':    5,
        },
    ]
    return render(request, 'core/about.html', {'volunteers': volunteers})


def contact(request):
    """Contact page."""
    return render(request, 'core/contact.html')