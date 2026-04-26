#Donations views 

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Donation, TREES_PER_DOLLAR
from core.models import ActivityEvent
from shop.views import _display_name


@login_required
@require_POST
def donate(request):
    #Process a donation POST 
    try:
        amount  = float(request.POST.get('amount', 0))
        message = request.POST.get('message', '').strip()[:300]

        if amount < 1:
            return JsonResponse({'error': 'Minimum donation is $1.'}, status=400)
        if amount > 10000:
            return JsonResponse({'error': 'Maximum single donation is $10,000.'}, status=400)

        donation = Donation.objects.create(
            user=request.user,
            amount=amount,
            message=message,
        )

        ActivityEvent.objects.create(
            event_type='donate',
            text=f'<strong>{_display_name(request.user)}</strong> donated ${amount:.0f} — planting {donation.trees_equivalent} trees',
            tag='complete', label='Donation',
            user=request.user
        )

        return JsonResponse({
            'success':          True,
            'trees_equivalent': donation.trees_equivalent,
            'amount':           str(donation.amount),
        })

    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid amount.'}, status=400)