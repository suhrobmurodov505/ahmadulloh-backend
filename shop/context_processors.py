from django.conf import settings


def site_settings(request):
    """Barcha shablonlarda SITE_NAME va savatchadagi mahsulotlar sonini mavjud qiladi."""
    cart_count = 0
    from .models import Cart
    if request.user.is_authenticated:
        cart_obj = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        cart_obj = Cart.objects.filter(session_key=session_key, user__isnull=True).first() if session_key else None
    if cart_obj:
        cart_count = sum(item.quantity for item in cart_obj.items.all())
    return {
        'SITE_NAME': settings.SITE_NAME,
        'cart_count': cart_count,
    }
