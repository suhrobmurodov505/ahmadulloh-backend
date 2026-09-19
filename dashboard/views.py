from django.shortcuts import render, redirect, get_object_or_404
from .decorators import staff_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from shop.models import Product, Category, Order, OrderItem
from shop.forms import ProductForm, CategoryForm


def _dashboard_stats():
    """Bazadan har chaqirilganda YANGI hisoblanadigan real vaqtdagi statistika."""
    paid_orders = Order.objects.filter(paid=True).prefetch_related('items')
    total_revenue = sum(order.get_total_cost() for order in paid_orders)
    return {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_revenue': total_revenue,
        'pending_orders': Order.objects.filter(status=Order.STATUS_PENDING).count(),
    }


@staff_required
def dashboard_home(request):
    """Admin panel bosh sahifasi: umumiy statistika."""
    context = _dashboard_stats()
    context.update({
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:8],
        'low_stock_products': Product.objects.filter(stock__lte=5, available=True).order_by('stock')[:6],
    })
    return render(request, 'dashboard/index.html', context)


@staff_required
def dashboard_stats_json(request):
    """Bosh sahifadagi statistik kartalarni sahifani qayta yuklamasdan
    (AJAX orqali) yangilab turish uchun JSON endpoint."""
    data = _dashboard_stats()
    data['server_time'] = timezone.now().strftime('%H:%M:%S')
    return JsonResponse(data)


# ---------- Mahsulot CRUD ----------

@staff_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'dashboard/product_list.html', {'products': products})


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot muvaffaqiyatli qo'shildi.")
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': "Yangi mahsulot qo'shish"})


@staff_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mahsulot yangilandi.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Mahsulotni tahrirlash'})


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Mahsulot o'chirildi.")
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': product, 'title': "Mahsulotni o'chirish"})


# ---------- Kategoriya CRUD ----------

@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategoriya qo'shildi.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': "Yangi kategoriya"})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategoriya yangilandi.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Kategoriyani tahrirlash'})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Kategoriya o'chirildi.")
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': category, 'title': "Kategoriyani o'chirish"})


# ---------- Buyurtmalar ----------

@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter or '',
    })


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        paid = request.POST.get('paid') == 'on'
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
        order.paid = paid
        order.save()
        messages.success(request, 'Buyurtma holati yangilandi.')
        return redirect('dashboard:order_detail', pk=pk)
    return render(request, 'dashboard/order_detail.html', {'order': order})


# ---------- Foydalanuvchilar boshqaruvi ----------

@staff_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/user_list.html', {'users': users})


@staff_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f"{user.username} holati o'zgartirildi.")
    return redirect('dashboard:user_list')


@staff_required
def user_toggle_staff(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_staff = not user.is_staff
        user.save()
        messages.success(request, f"{user.username} admin huquqi o'zgartirildi.")
    return redirect('dashboard:user_list')


# ---------- Hisobotlar ----------

@staff_required
def reports(request):
    """Sotuvlar hisoboti: oxirgi 14 kunlik sotuv, eng ko'p sotilgan mahsulotlar."""
    since = timezone.now() - timedelta(days=14)

    daily_sales = (
        Order.objects.filter(created_at__gte=since, paid=True)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(orders_count=Count('id'))
        .order_by('day')
    )

    top_products = (
        OrderItem.objects.values('product_name')
        .annotate(total_sold=Sum('quantity'), total_revenue=Sum(F('price') * F('quantity')))
        .order_by('-total_sold')[:8]
    )

    status_labels = dict(Order.STATUS_CHOICES)
    status_breakdown = [
        {'status': status_labels.get(row['status'], row['status']), 'count': row['count']}
        for row in Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    ]

    return render(request, 'dashboard/reports.html', {
        'daily_sales': list(daily_sales),
        'top_products': top_products,
        'status_breakdown': status_breakdown,
    })
