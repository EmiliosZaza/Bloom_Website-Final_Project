"""
Catalogue views — product review submission
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Product, Review


@login_required
@require_POST
def submit_review(request, product_id):
    """Submit or update a star rating and review for a product"""
    product = get_object_or_404(Product, pk=product_id)
    stars   = int(request.POST.get('stars', 0))
    text    = request.POST.get('text', '').strip()[:500]

    # Server-side validation
    if stars < 1 or stars > 5:
        return JsonResponse({'error': 'Rating must be between 1 and 5.'}, status=400)

    # update_or_create — one review per user per product
    Review.objects.update_or_create(
        product=product, user=request.user,
        defaults={'stars': stars, 'text': text}
    )
    return JsonResponse({'success': True, 'avg_rating': product.avg_rating})
