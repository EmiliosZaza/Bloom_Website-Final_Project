def cart_count(request):
    #Inject cart item count into every template context
    count = 0
    if request.user.is_authenticated:
        from shop.models import CartItem
        count = CartItem.objects.filter(user=request.user).count()
    return {'cart_count': count}
