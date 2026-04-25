"""
Accounts views — login, register, logout, profile, dashboard
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from catalogue.models import Product, WishlistItem
from shop.models import Order, OrderItem
from donations.models import TREES_PER_DOLLAR
from .models import ViewedProduct


def login_view(request):
    """Handle login form POST — redirects back to the page the user came from"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '/')

        if not username or not password:
            return redirect(f'/?login_error=Please+fill+in+all+fields&open_auth=login&next={next_url}')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url or '/')
        else:
            return redirect(f'/?login_error=Invalid+username+or+password&open_auth=login&next={next_url}')

    return redirect('core:home')


def register_view(request):
    """Handle registration form POST"""
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            return redirect('/?register_error=Please+fill+in+all+required+fields&open_auth=register')
        if password1 != password2:
            return redirect('/?register_error=Passwords+do+not+match&open_auth=register')
        if len(password1) < 8:
            return redirect('/?register_error=Password+must+be+at+least+8+characters&open_auth=register')
        if User.objects.filter(username=username).exists():
            return redirect('/?register_error=Username+already+taken&open_auth=register')
        if User.objects.filter(email=email).exists():
            return redirect('/?register_error=Email+already+registered&open_auth=register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
        )
        login(request, user)
        return redirect('core:home')

    return redirect('core:home')


def logout_view(request):
    """One-click logout via POST form"""
    if request.method == 'POST':
        logout(request)
    return redirect('core:home')


@login_required
def profile(request):
    """View and update profile info"""
    if request.method == 'POST':
        user       = request.user
        first_name = request.POST.get('first_name', '').strip()[:150]
        last_name  = request.POST.get('last_name', '').strip()[:150]
        bio        = request.POST.get('bio', '').strip()[:300]

        user.first_name = first_name
        user.last_name  = last_name
        user.save()

        profile = user.profile
        profile.bio = bio
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        profile.save()

        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'profile': request.user.profile})


@login_required
def dashboard(request):
    """Personal dashboard — orders, donations, wishlist, viewed products"""
    user = request.user

    user_orders    = Order.objects.filter(user=user)
    purchase_trees = sum(
        int(item.price * item.quantity * TREES_PER_DOLLAR)
        for order in user_orders
        for item in order.items.all()
    )
    donation_trees = sum(d.trees_equivalent for d in user.donations.all())
    my_trees       = purchase_trees + donation_trees

    context = {
        'orders':    user_orders[:5],
        'donations': user.donations.all()[:5],
        'wishlist':  WishlistItem.objects.filter(user=user).select_related('product')[:8],
        'viewed':    ViewedProduct.objects.filter(user=user).select_related('product')[:8],
        'my_trees':  my_trees,
    }
    return render(request, 'accounts/dashboard.html', context)


def record_view(request, product_id):
    """AJAX — record a product view for the recommender system"""
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(pk=product_id)
            ViewedProduct.objects.update_or_create(user=request.user, product=product)
        except Product.DoesNotExist:
            pass
    return JsonResponse({'ok': True})