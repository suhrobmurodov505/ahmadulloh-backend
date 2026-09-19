from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('statistika.json', views.dashboard_stats_json, name='stats_json'),

    path('mahsulotlar/', views.product_list, name='product_list'),
    path('mahsulotlar/qoshish/', views.product_create, name='product_create'),
    path('mahsulotlar/<int:pk>/tahrirlash/', views.product_update, name='product_update'),
    path('mahsulotlar/<int:pk>/ochirish/', views.product_delete, name='product_delete'),

    path('kategoriyalar/', views.category_list, name='category_list'),
    path('kategoriyalar/qoshish/', views.category_create, name='category_create'),
    path('kategoriyalar/<int:pk>/tahrirlash/', views.category_update, name='category_update'),
    path('kategoriyalar/<int:pk>/ochirish/', views.category_delete, name='category_delete'),

    path('buyurtmalar/', views.order_list, name='order_list'),
    path('buyurtmalar/<int:pk>/', views.order_detail, name='order_detail'),

    path('foydalanuvchilar/', views.user_list, name='user_list'),
    path('foydalanuvchilar/<int:pk>/faollik/', views.user_toggle_active, name='user_toggle_active'),
    path('foydalanuvchilar/<int:pk>/admin-huquqi/', views.user_toggle_staff, name='user_toggle_staff'),

    path('hisobotlar/', views.reports, name='reports'),
]
