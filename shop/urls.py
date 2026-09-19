from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('sayt/', views.spa, name='spa'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/categories/', views.api_categories, name='api_categories'),

    path('kategoriyalar/', views.category_list, name='category_list'),

    path('mahsulotlar/', views.product_list, name='product_list'),
    path('mahsulotlar/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('mahsulot/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    path('savatcha/', views.cart_detail, name='cart_detail'),
    path('savatcha/qoshish/<int:product_id>/', views.cart_add, name='cart_add'),
    path('savatcha/yangilash/<int:item_id>/', views.cart_update, name='cart_update'),
    path('savatcha/ochirish/<int:item_id>/', views.cart_remove, name='cart_remove'),

    path('buyurtma/', views.order_create, name='order_create'),
    path('buyurtmalarim/', views.order_history, name='order_history'),
    path('buyurtmalarim/<int:order_id>/', views.order_detail, name='order_detail'),
]
