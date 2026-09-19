from .models import Cart, CartItem, Product


def _ensure_session_key(request):
    """Brauzer sessiyasi mavjud emasligini tekshiradi va kerak bo'lsa yaratadi."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart(request):
    """Foydalanuvchi (tizimga kirgan) yoki mehmon (anonim) uchun savatchani qaytaradi.

    Tizimga kirgan foydalanuvchi uchun `user` bo'yicha, mehmon uchun esa
    brauzer sessiyasi (`session_key`) bo'yicha saqlanadi — shu sababli
    savatchadan foydalanish uchun tizimga kirish talab qilinmaydi.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Agar foydalanuvchi mehmon bo'lganida savatchaga mahsulot qo'shgan
        # bo'lsa, tizimga kirgach ular ham shu savatchaga qo'shiladi.
        session_key = request.session.session_key
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).exclude(id=cart.id).first()
            if guest_cart:
                for item in guest_cart.items.all():
                    existing = cart.items.filter(product=item.product).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                guest_cart.delete()
        return cart

    session_key = _ensure_session_key(request)
    cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def add_to_cart(request, product_id, quantity=1, override_quantity=False):
    cart = get_cart(request)
    product = Product.objects.get(id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        if override_quantity:
            item.quantity = quantity
        else:
            item.quantity += quantity
        item.save()
    return item


def remove_from_cart(request, item_id):
    cart = get_cart(request)
    CartItem.objects.filter(cart=cart, id=item_id).delete()


def update_cart_item(request, item_id, quantity):
    cart = get_cart(request)
    CartItem.objects.filter(cart=cart, id=item_id).update(quantity=quantity)


def clear_cart(request):
    get_cart(request).items.all().delete()
