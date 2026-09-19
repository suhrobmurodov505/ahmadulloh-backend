# Frontendni Django bilan ulash — qo'llanma

Bosh sahifa (`templates/base.html` + `shop/templates/shop/home.html`) allaqachon
ulab berildi. Qolgan sahifalaringizni ham xuddi shu naqsh (pattern) bo'yicha
o'zingiz ulashingiz mumkin. Quyida aniq qadamlar.

## 1. Fayl nomini yuboring, men qaysi Django view'ga tegishli ekanini aytaman

| Sizning sahifangiz | Tayyor Django shabloni (qayerga joylash) | View |
|---|---|---|
| Mahsulotlar ro'yxati | `shop/templates/shop/product_list.html` | `shop/views.py` → `product_list` |
| Mahsulot tafsilotlari | `shop/templates/shop/product_detail.html` | `product_detail` |
| Kategoriyalar | `shop/templates/shop/category_list.html` | `category_list` |
| Savatcha | `shop/templates/shop/cart_detail.html` | `cart_detail` |
| Checkout | `shop/templates/shop/order_create.html` | `order_create` |
| Profil | `accounts/templates/accounts/profile.html` | `accounts/views.py` → `profile` |
| Buyurtmalar tarixi | `shop/templates/shop/order_history.html` | `order_history` |
| Kirish | `accounts/templates/accounts/login.html` | `VertexLoginView` |
| Ro'yxatdan o'tish | `accounts/templates/accounts/register.html` | `register` |

Bu fayllar hozir ham mavjud, lekin **oddiy uslubda** (sizning yangi dizayningiz
bilan emas). Har birini menga yuboring — men ularni bosh sahifadagi kabi
sizning Tailwind dizayningizga moslab qayta yozib beraman.

## 2. Har bir sahifada takrorlanadigan 3 ta qadam

Har qanday yangi HTML faylni menga yuborganingizda, men ichida shularni qilaman:

1. **`<!DOCTYPE html>` dan `<body>` gacha bo'lgan qismni olib tashlayman** —
   chunki bu allaqachon `base.html` da bor. Faqat ichki kontent qoladi.
2. **`{% extends "base.html" %}` va `{% block content %}...{% endblock %}`**
   bilan o'rayman.
3. **Statik (qotib qolgan) ma'lumotlarni** bazadan keladigan Django teglariga
   almashtiraman — masalan sizda qo'lda yozilgan mahsulot nomi/narxi bo'lsa,
   uni `{{ product.name }}`, `{{ product.price }}` bilan almashtiraman.

## 3. Rasmlar haqida

- Sayt logotipi (`vertex png.png`) ni **`static/img/vertex.png`** deb nomlab
  o'sha papkaga joylang (nom aynan shunday, kichik harflarda).
- Boshqa doimiy dizayn elementlari (fon rasmlari, ikonkalar) ham
  `static/img/` ichiga joylanadi.
- Mahsulot va kategoriya rasmlari esa **bazaga admin panel orqali
  yuklanadi** (`/dashboard/mahsulotlar/qoshish/`) — ular avtomatik
  `media/` papkasiga saqlanadi, kodda qo'lda yozish shart emas.

## 4. Savatcha/like tugmalari haqida eslatma

Bosh sahifada "Savatga" tugmasi endi haqiqiy `POST` so'rovi yuboradi va
mahsulotni bazadagi savatchaga qo'shadi. Agar sizda "like/sevimlilar"
funksiyasi rejalashtirilgan bo'lsa (yurak belgisi), buning uchun alohida
`Wishlist` modeli kerak bo'ladi — hozircha u faqat bezak sifatida qoldirildi,
bosilganda hech narsa saqlanmaydi. Kerak bo'lsa, aytib qo'ying — qo'shib
beraman.
