from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Category, Product, Order, OrderItem
from .cart import get_cart, add_to_cart, remove_from_cart, update_cart_item, clear_cart
from .forms import CartAddProductForm, OrderCreateForm


def spa(request):
    """Sizning SPA frontendingizni ko'rsatadi (index.html). Ma'lumotlar JS orqali /api/ dan olinadi."""
    return render(request, 'shop/spa.html')


def api_products(request):
    """Barcha sotuvdagi mahsulotlarni JSON qilib qaytaradi (frontend shu yerdan o'qiydi)."""
    products = Product.objects.filter(available=True).select_related('category')
    data = []
    for p in products:
        data.append({
            'id': p.id,
            'name': p.name,
            'category': p.category.name,
            'price': float(p.price),
            'stock': p.stock,
            'image': request.build_absolute_uri(p.image.url) if p.image else '',
        })
    return JsonResponse(data, safe=False)


def api_categories(request):
    """Barcha kategoriyalarni JSON qilib qaytaradi."""
    categories = Category.objects.all()
    data = [{'id': c.id, 'name': c.name, 'count': c.product_count} for c in categories]
    return JsonResponse(data, safe=False)


def home(request):
    """Bosh sahifa: kategoriyalar va so'nggi mahsulotlar."""
    categories = Category.objects.all()[:4]
    products = Product.objects.filter(available=True)[:10]
    return render(request, 'shop/home.html', {
        'categories': categories,
        'products': products,
        'total_products': Product.objects.filter(available=True).count(),
    })


def category_list(request):
    """Barcha kategoriyalar sahifasi."""
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})


def product_list(request, category_slug=None):
    """Barcha mahsulotlar ro'yxati, kategoriya bo'yicha filter va qidiruv bilan."""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'query': query or '',
    })


def product_detail(request, id, slug):
    """Bitta mahsulot haqida to'liq ma'lumot."""
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    similar_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'similar_products': similar_products,
    })


@require_POST
def cart_add(request, product_id):
    """Mahsulotni savatchaga qo'shish (tizimga kirish shart emas — mehmon
    uchun ham brauzer sessiyasi orqali ishlaydi)."""
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        add_to_cart(request, product_id, quantity=cd['quantity'], override_quantity=cd['override'])
        messages.success(request, 'Mahsulot savatchaga qo\'shildi.')
    return redirect('shop:cart_detail')


@require_POST
def cart_remove(request, item_id):
    remove_from_cart(request, item_id)
    return redirect('shop:cart_detail')


@require_POST
def cart_update(request, item_id):
    quantity = request.POST.get('quantity', 1)
    try:
        quantity = max(1, int(quantity))
    except (TypeError, ValueError):
        quantity = 1
    update_cart_item(request, item_id, quantity)
    return redirect('shop:cart_detail')


def cart_detail(request):
    """Savatcha tarkibini ko'rsatish (mehmon uchun ham ishlaydi)."""
    cart = get_cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


def order_create(request):
    """Buyurtma berish: savatchadagi mahsulotlardan buyurtma yaratiladi.

    Tizimga kirgan foydalanuvchi ham, mehmon (anonim) ham buyurtma bera oladi.
    """
    cart = get_cart(request)
    if cart.items.count() == 0:
        return redirect('shop:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.session_key = request.session.session_key
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                # Ombordan kamaytiramiz
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()
            clear_cart(request)
            return render(request, 'shop/order_created.html', {'order': order})
    else:
        initial = {}
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            initial = {
                'full_name': request.user.get_full_name() or request.user.username,
                'phone': getattr(profile, 'phone', ''),
                'address': getattr(profile, 'address', ''),
            }
        form = OrderCreateForm(initial=initial)

    return render(request, 'shop/order_create.html', {'cart': cart, 'form': form})


def order_history(request):
    """Foydalanuvchining (yoki mehmonning) barcha buyurtmalari tarixi."""
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
    else:
        session_key = request.session.session_key
        orders = Order.objects.filter(session_key=session_key).prefetch_related('items') if session_key else Order.objects.none()
    return render(request, 'shop/order_history.html', {'orders': orders})


def order_detail(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        session_key = request.session.session_key
        order = get_object_or_404(Order, id=order_id, session_key=session_key, user__isnull=True)
    return render(request, 'shop/order_detail.html', {'order': order})
