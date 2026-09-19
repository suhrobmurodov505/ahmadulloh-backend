# VERTEX — Onlayn Do'kon Backend (Django)

To'liq funksional Django backend: autentifikatsiya, mahsulot/kategoriya CRUD,
bazaga asoslangan savatcha, buyurtmalar tizimi, foydalanuvchi profili va
buyurtmalar tarixi, hamda alohida Admin Dashboard (boshqaruv paneli) va
hisobotlar tizimi.

## Loyiha tuzilishi

```
myshop/
├── manage.py
├── requirements.txt
├── config/                    -> loyiha sozlamalari (settings, urls)
├── shop/                      -> Mahsulot, Kategoriya, Savatcha, Buyurtma
│   ├── models.py              -> Category, Product, Cart, CartItem, Order, OrderItem
│   ├── views.py, urls.py, forms.py, cart.py
│   └── templates/shop/
├── accounts/                  -> Autentifikatsiya va foydalanuvchi profili
│   ├── models.py              -> Profile (User kengaytmasi)
│   ├── views.py, urls.py, forms.py
│   └── templates/accounts/
├── dashboard/                 -> Admin Dashboard (faqat staff uchun)
│   ├── views.py               -> CRUD, foydalanuvchilar, hisobotlar
│   └── templates/dashboard/
├── templates/base.html        -> umumiy sayt shabloni (header/footer)
└── static/css/                -> style.css (sayt), dashboard.css (panel)
```

## DATABASE jadvallari (modellar)

| Talab qilingan jadval | Loyihadagi model |
|---|---|
| Users | Django `User` + `accounts.Profile` |
| Categories | `shop.Category` |
| Products | `shop.Product` |
| Cart | `shop.Cart` |
| Cart Items | `shop.CartItem` |
| Orders | `shop.Order` |
| Order Items | `shop.OrderItem` |

## BACKEND MODULLARI

- **Authentication System** — `accounts` ilovasi: ro'yxatdan o'tish, kirish, chiqish
- **Product CRUD** — `dashboard` orqali (qo'shish/tahrirlash/o'chirish), o'qish hamma uchun ochiq
- **Category CRUD** — `dashboard` orqali
- **Cart System** — `shop.cart` (bazaga asoslangan, har bir foydalanuvchi uchun alohida)
- **Order System** — checkout, holat (status), buyurtmalar tarixi
- **User Management** — `dashboard`: foydalanuvchilarni bloklash/faollashtirish, admin huquqi berish
- **Reports System** — `dashboard/hisobotlar/`: kunlik sotuvlar, eng ko'p sotilgan mahsulotlar, holat bo'yicha taqsimot

## FRONTEND SAHIFALARI

| Sahifa | URL |
|---|---|
| Bosh sahifa | `/` |
| Mahsulotlar | `/mahsulotlar/` |
| Mahsulot tafsilotlari | `/mahsulot/<id>/<slug>/` |
| Kategoriyalar | `/kategoriyalar/` |
| Savatcha | `/savatcha/` |
| Buyurtmani rasmiylashtirish | `/buyurtma/` |
| Foydalanuvchi profili | `/accounts/profil/` |
| Buyurtmalar tarixi | `/buyurtmalarim/` |
| Admin Dashboard | `/dashboard/` |

## PyCharmda ishga tushirish

1. **Loyihani oching**: `File → Open` orqali `myshop` papkasini oching.

2. **Virtual muhit**:
   ```
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Kutubxonalarni o'rnatish**:
   ```
   pip install -r requirements.txt
   ```

4. **Bazani yaratish**:
   ```
   python manage.py migrate
   ```

5. **Superuser (admin) yaratish**:
   ```
   python manage.py createsuperuser
   ```

6. **Serverni ishga tushirish**:
   ```
   python manage.py runserver
   ```

7. Brauzerda:
   - Sayt: http://127.0.0.1:8000/
   - Admin Dashboard (boshqaruv paneli): http://127.0.0.1:8000/dashboard/
   - Django texnik admin: http://127.0.0.1:8000/django-admin/

## Ishlatish tartibi

1. `createsuperuser` bilan yaratilgan hisob avtomatik `is_staff=True` bo'lgani
   uchun `/dashboard/`ga kira oladi.
2. Dashboard orqali **Kategoriya** va **Mahsulot** qo'shing.
3. Oddiy foydalanuvchi `/accounts/royxatdan-otish/` orqali ro'yxatdan o'tadi,
   mahsulotlarni ko'radi, savatchaga qo'shadi va buyurtma beradi.
4. Admin `/dashboard/buyurtmalar/` bo'limida buyurtma holatini
   ("Kutilmoqda" → "Tayyorlanmoqda" → "Yuborildi" → "Yetkazildi") o'zgartiradi.
5. `/dashboard/foydalanuvchilar/` orqali foydalanuvchilarni bloklash yoki
   ularga admin huquqi berish mumkin.
6. `/dashboard/hisobotlar/` — sotuvlar statistikasi.

## O'zingizning frontendingizni ulash

1. `templates/base.html` dagi `<header>`/`<footer>`ni o'z HTML kodingiz bilan almashtiring.
2. `static/css/style.css` o'rniga o'z CSS fayllaringizni joylashtiring.
3. Har bir sahifadagi `{% block content %}...{% endblock %}` ichini
   moslang, lekin Django teglarini (`{{ product.name }}`, `{% url %}`,
   `{% for %}`) saqlab qoling.
4. `dashboard/` ilovasining shablonlari (`static/css/dashboard.css`) alohida,
   sizning asosiy sayt dizayningizga bog'liq emas — xohlasangiz uni ham
   o'zgartirishingiz mumkin.

## Muhim eslatma

- `DEBUG = True` va `SECRET_KEY` faqat lokal ishlatish uchun. Production'ga
  chiqarishdan oldin ularni `.env` fayl orqali maxfiy saqlang va
  `DEBUG = False`, to'g'ri `ALLOWED_HOSTS` qo'ying.
- Savatcha endi **bazada** saqlanadi (har bir `User`ga bitta `Cart`) — shuning
  uchun savatcha va buyurtma berish uchun tizimga kirish shart.
