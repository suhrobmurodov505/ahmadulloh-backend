from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    """Mahsulot kategoriyasi (masalan: Telefonlar, Kiyimlar)."""
    name = models.CharField('Nomi', max_length=200)
    slug = models.SlugField('Slug (URL uchun)', max_length=200, unique=True)
    description = models.TextField('Tavsif', blank=True)
    image = models.ImageField('Rasm', upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

    @property
    def product_count(self):
        return self.products.filter(available=True).count()


class Product(models.Model):
    """Sotuvdagi mahsulot."""
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name='Kategoriya'
    )
    name = models.CharField('Nomi', max_length=255)
    slug = models.SlugField('Slug (URL uchun)', max_length=255, unique=True)
    description = models.TextField('Tavsif', blank=True)
    image = models.ImageField('Rasm', upload_to='products/%Y/%m/', blank=True, null=True)
    price = models.DecimalField("Narxi (so'm)", max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField('Ombordagi soni', default=0)
    available = models.BooleanField('Sotuvda bormi', default=True)
    created_at = models.DateTimeField("Qo'shilgan sana", auto_now_add=True)
    updated_at = models.DateTimeField('Yangilangan sana', auto_now=True)

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


class Cart(models.Model):
    """Har bir foydalanuvchining (yoki mehmonning) bazadagi savatchasi.

    Tizimga kirgan foydalanuvchi uchun `user` orqali, mehmon (anonim) uchun
    esa brauzer sessiyasi (`session_key`) orqali aniqlanadi — shu sababli
    savatchadan foydalanish uchun tizimga kirish shart emas.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField('Sessiya kaliti', max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Savatcha'
        verbose_name_plural = 'Savatchalar'

    def __str__(self):
        return f"{self.user.username} savatchasi" if self.user else f"Mehmon savatchasi ({self.session_key})"

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Savatcha ichidagi bitta mahsulot qatori."""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Soni', default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Savatcha elementi'
        verbose_name_plural = 'Savatcha elementlari'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Mijoz buyurtmasi.

    Tizimga kirgan foydalanuvchi uchun `user` orqali, mehmon (anonim) buyurtma
    uchun esa `session_key` orqali bog'lanadi — buyurtma berish uchun tizimga
    kirish shart emas.
    """

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Kutilmoqda'),
        (STATUS_PROCESSING, 'Tayyorlanmoqda'),
        (STATUS_SHIPPED, 'Yuborildi'),
        (STATUS_DELIVERED, 'Yetkazildi'),
        (STATUS_CANCELLED, 'Bekor qilindi'),
    ]

    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, verbose_name='Foydalanuvchi', null=True, blank=True)
    session_key = models.CharField('Sessiya kaliti', max_length=40, null=True, blank=True, db_index=True)
    full_name = models.CharField('F.I.Sh.', max_length=255)
    phone = models.CharField('Telefon raqami', max_length=32)
    address = models.CharField('Manzil', max_length=500)
    comment = models.TextField('Izoh', blank=True)
    status = models.CharField('Holati', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField('Buyurtma sanasi', auto_now_add=True)
    paid = models.BooleanField("To'landimi", default=False)

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f'Buyurtma #{self.id} — {self.full_name}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_status_display_class(self):
        """Shablonda status uchun CSS klass tanlash."""
        return {
            self.STATUS_PENDING: 'status-pending',
            self.STATUS_PROCESSING: 'status-processing',
            self.STATUS_SHIPPED: 'status-shipped',
            self.STATUS_DELIVERED: 'status-delivered',
            self.STATUS_CANCELLED: 'status-cancelled',
        }.get(self.status, '')


class OrderItem(models.Model):
    """Buyurtma ichidagi bitta mahsulot qatori."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, help_text="Mahsulot o'chirilsa ham nomi saqlanib qoladi")
    price = models.DecimalField('Narxi', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('Soni', default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.name
        super().save(*args, **kwargs)
