from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """staff_member_required'ga o'xshaydi, lekin Django'ning standart
    /django-admin/login/ sahifasiga emas, bizning shaxsiy (Vertex dizaynidagi)
    login sahifamizga (settings.LOGIN_URL = 'accounts:login') yo'naltiradi."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Bu sahifaga faqat administratorlar kira oladi.")
        return view_func(request, *args, **kwargs)

    return _wrapped
