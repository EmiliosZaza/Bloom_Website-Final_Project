#custom error handlers

from django.shortcuts import render


def handler404(request, exception=None):
    """Custom 404 — page not found"""
    return render(request, '404.html', status=404)


def handler403(request, exception=None):
    """Custom 403 — permission denied"""
    return render(request, '403.html', status=403)
