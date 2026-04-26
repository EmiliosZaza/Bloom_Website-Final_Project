#Admin panel views - custom interface for staff only. All views protected by staff_required decorator.


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from catalogue.models import Category, Subcategory, Product
from core.models import ActivityEvent
from core.views import get_total_trees
from shop.models import Order
from donations.models import Donation


def staff_required(view_func):
    #Decorator: redirect guests to login, raise 403 for logged-in non-staff users.
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped


@staff_required
def dashboard(request):
    #Admin overview - key stats at a glance.
    context = {
        'total_users':      User.objects.count(),
        'total_products':   Product.objects.count(),
        'total_orders':     Order.objects.count(),
        'total_donations':  Donation.objects.count(),
        'total_trees':      get_total_trees(),
        'recent_orders':    Order.objects.select_related('user').order_by('-created_at')[:5],
        'recent_donations': Donation.objects.select_related('user').order_by('-created_at')[:5],
    }
    return render(request, 'panel/dashboard.html', context)


@staff_required
def products(request):
    #List all products with optional search.
    q  = request.GET.get('q', '').strip()
    qs = Product.objects.select_related('category', 'subcategory').order_by('-created_at')
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, 'panel/products.html', {'products': qs, 'q': q})


@staff_required
def product_add(request):
    #Add a new product with image upload.
    categories    = Category.objects.all()
    subcategories = Subcategory.objects.all()

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()[:120]
        description = request.POST.get('description', '').strip()[:1000]
        price       = request.POST.get('price', '0')
        stock       = request.POST.get('stock', '0')
        cat_id      = request.POST.get('category')
        subcat_id   = request.POST.get('subcategory')
        tags        = request.POST.get('tags', '').strip()[:200]
        is_active   = request.POST.get('is_active') == 'on'

        errors = []
        if len(name) < 2:  errors.append('Name must be at least 2 characters.')
        if not price:      errors.append('Price is required.')
        try:
            price = float(price)
            if price < 0: errors.append('Price cannot be negative.')
        except ValueError: errors.append('Price must be a number.')

        if errors:
            return render(request, 'panel/product_form.html', {
                'errors': errors, 'categories': categories,
                'subcategories': subcategories, 'action': 'Add'
            })

        product = Product(
            name=name, description=description, price=price,
            stock=int(stock or 0), tags=tags, is_active=is_active
        )
        if cat_id:    product.category_id    = int(cat_id)
        if subcat_id: product.subcategory_id = int(subcat_id)
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        return redirect('panel:products')

    return render(request, 'panel/product_form.html', {
        'categories': categories, 'subcategories': subcategories, 'action': 'Add'
    })


@staff_required
def product_edit(request, product_id):
    #Edit an existing product.
    product       = get_object_or_404(Product, pk=product_id)
    categories    = Category.objects.all()
    subcategories = Subcategory.objects.all()

    if request.method == 'POST':
        product.name        = request.POST.get('name', '').strip()[:120]
        product.description = request.POST.get('description', '').strip()[:1000]
        product.tags        = request.POST.get('tags', '').strip()[:200]
        product.stock       = int(request.POST.get('stock', 0) or 0)
        product.is_active   = request.POST.get('is_active') == 'on'
        cat_id    = request.POST.get('category')
        subcat_id = request.POST.get('subcategory')
        try:
            product.price = float(request.POST.get('price', product.price))
        except ValueError:
            pass
        product.category_id    = int(cat_id)    if cat_id    else None
        product.subcategory_id = int(subcat_id) if subcat_id else None
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        return redirect('panel:products')

    return render(request, 'panel/product_form.html', {
        'product': product, 'categories': categories,
        'subcategories': subcategories, 'action': 'Edit'
    })


@staff_required
def product_delete(request, product_id):
    #Confirm and delete a product.
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('panel:products')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': product.name, 'cancel_url': 'panel:products'
    })


@staff_required
def categories(request):
    #List all categories and their subcategories.
    cats = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'panel/categories.html', {'categories': cats})


@staff_required
def category_add(request):
    #Add a new category.
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()[:80]
        desc = request.POST.get('description', '').strip()
        if name:
            Category.objects.create(name=name, description=desc)
        return redirect('panel:categories')
    return render(request, 'panel/category_form.html', {'action': 'Add Category'})


@staff_required
def category_delete(request, cat_id):
    #Confirm and delete a category.
    cat = get_object_or_404(Category, pk=cat_id)
    if request.method == 'POST':
        cat.delete()
        return redirect('panel:categories')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': cat.name, 'cancel_url': 'panel:categories'
    })


@staff_required
def subcategory_add(request, cat_id):
    #Add a subcategory under an existing category.
    cat = get_object_or_404(Category, pk=cat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()[:80]
        if name:
            Subcategory.objects.create(name=name, category=cat)
        return redirect('panel:categories')
    return render(request, 'panel/category_form.html', {
        'action': f'Add Subcategory to {cat.name}', 'parent': cat
    })


@staff_required
def users(request):
    #List all users with optional search by username or email.
    q  = request.GET.get('q', '').strip()
    qs = User.objects.select_related('profile').order_by('-date_joined')
    if q:
        qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q)
    return render(request, 'panel/users.html', {'users': qs, 'q': q})


@staff_required
def user_toggle_staff(request, user_id):
    #Toggle staff status for a user. Cannot demote yourself.
    if request.method == 'POST':
        u = get_object_or_404(User, pk=user_id)
        if u != request.user:
            u.is_staff = not u.is_staff
            u.save()
    return redirect('panel:users')


@staff_required
def user_delete(request, user_id):
    #Confirm and delete a user. Cannot delete yourself.
    u = get_object_or_404(User, pk=user_id)
    if u == request.user:
        return redirect('panel:users')
    if request.method == 'POST':
        u.delete()
        return redirect('panel:users')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': u.username, 'cancel_url': 'panel:users'
    })