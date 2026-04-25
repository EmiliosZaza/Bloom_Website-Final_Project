"""
Shop views — support page, cart, checkout, wishlist, AJAX endpoints
Trees from purchases: price × quantity × 5 (computed at order time, not stored per product)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalogue.models import Product, Category, WishlistItem, Review
from accounts.models import ViewedProduct
from .models import CartItem, Order, OrderItem
from donations.models import Donation, TREES_PER_DOLLAR
from core.models import ActivityEvent
from core.views import get_total_trees


def _display_name(user):
    """Return full name if set, otherwise username."""
    return user.get_full_name() or user.username


def support(request):
    """Support Us page — shop + donate"""
    categories = Category.objects.prefetch_related('products').all()
    products   = Product.objects.filter(is_active=True).select_related('category', 'subcategory')

    cat_slug = request.GET.get('category', '')
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q) | products.filter(tags__icontains=q)

    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    products_list = list(products)
    for p in products_list:
        p.trees_per_purchase = int(p.price * TREES_PER_DOLLAR)

    return render(request, 'catalogue/support.html', {
        'products':          products_list,
        'categories':        categories,
        'selected_category': cat_slug,
        'search_query':      q,
        'min_price':         min_price,
        'max_price':         max_price,
        'wishlist_ids':      wishlist_ids,
        'trees_per_dollar':  TREES_PER_DOLLAR,
        'total_trees':       get_total_trees(),
    })


@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.subtotal for item in items)
    trees = int(total * TREES_PER_DOLLAR)
    return render(request, 'shop/cart.html', {'items': items, 'total': total, 'trees': trees})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = CartItem.objects.get_or_create(
        user=request.user, product=product,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'success': True, 'cart_count': cart_count})


@login_required
@require_POST
def remove_from_cart(request, item_id):
    CartItem.objects.filter(pk=item_id, user=request.user).delete()
    items = CartItem.objects.filter(user=request.user)
    total = sum(i.subtotal for i in items)
    trees = int(total * TREES_PER_DOLLAR)
    return JsonResponse({'success': True, 'total': str(total), 'trees': trees, 'cart_count': items.count()})


@login_required
@require_POST
def checkout(request):
    """Simulate a purchase — trees = total × 5"""
    items = CartItem.objects.filter(user=request.user).select_related('product')
    if not items.exists():
        return redirect('shop:cart')

    total         = sum(item.subtotal for item in items)
    order         = Order.objects.create(user=request.user, total=total, status='confirmed')
    trees_planted = 0

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
        item_trees     = int(item.product.price * item.quantity * TREES_PER_DOLLAR)
        trees_planted += item_trees

        ActivityEvent.objects.create(
            event_type='purchase',
            text=f'<strong>{_display_name(request.user)}</strong> purchased {item.product.name} — planting {item_trees} trees',
            tag='complete', label='Purchase',
            user=request.user
        )

    items.delete()
    return redirect('shop:order_confirmation', order_id=order.id)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.items.select_related('product')
    trees = int(order.total * TREES_PER_DOLLAR)
    return render(request, 'shop/order_confirmation.html', {
        'order': order,
        'items': items,
        'trees': trees,
    })


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        return JsonResponse({'success': True, 'wishlisted': False})
    return JsonResponse({'success': True, 'wishlisted': True})


def product_detail_ajax(request, product_id):
    """AJAX — product detail for quick-view modal"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.user.is_authenticated:
        ViewedProduct.objects.update_or_create(user=request.user, product=product)

    similar = list(
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product_id)[:4]
        .values('id', 'name', 'price', 'image')
    )
    for p in similar:
        p['price'] = str(p['price'])
        p['trees'] = int(float(p['price']) * TREES_PER_DOLLAR)
        p['image'] = '/media/' + p['image'] if p['image'] else ''

    wishlisted = False
    user_review = None
    if request.user.is_authenticated:
        wishlisted = WishlistItem.objects.filter(user=request.user, product=product).exists()
        try:
            existing = Review.objects.get(product=product, user=request.user)
            user_review = {'stars': existing.stars, 'text': existing.text}
        except Review.DoesNotExist:
            pass

    reviews = [
        {
            'username': r.user.username,
            'stars':    r.stars,
            'text':     r.text,
            'date':     r.created_at.strftime('%d %b %Y'),
        }
        for r in product.reviews.select_related('user').all()[:5]
    ]

    trees = int(product.price * TREES_PER_DOLLAR)

    return JsonResponse({
        'id':          product.id,
        'name':        product.name,
        'description': product.description,
        'price':       str(product.price),
        'trees':       trees,
        'image':       product.image.url if product.image else '',
        'stock':       product.stock,
        'category':    product.category.name if product.category else '',
        'avg_rating':  product.avg_rating,
        'wishlisted':  wishlisted,
        'similar':     similar,
        'reviews':     reviews,
        'user_review': user_review,
    })