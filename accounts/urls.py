from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('royxatdan-otish/', views.register, name='register'),
    path('kirish/', views.VertexLoginView.as_view(), name='login'),
    path('chiqish/', views.VertexLogoutView.as_view(), name='logout'),
    path('profil/', views.profile, name='profile'),
]
