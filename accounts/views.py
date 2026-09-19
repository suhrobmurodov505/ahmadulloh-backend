from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import RegisterForm, ProfileUpdateForm, UserUpdateForm


def register(request):
    """Yangi foydalanuvchini ro'yxatdan o'tkazish."""
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}! Ro'yxatdan muvaffaqiyatli o'tdingiz.")
            return redirect('shop:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class VertexLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class VertexLogoutView(LogoutView):
    next_page = reverse_lazy('shop:home')


def profile(request):
    """Foydalanuvchi profilini ko'rish va tahrirlash.

    Tizimga kirmagan (mehmon) foydalanuvchi uchun sahifa parol so'ramaydi —
    o'rniga kirish/ro'yxatdan o'tishga taklif qiluvchi "mehmon" ko'rinishi
    ko'rsatiladi.
    """
    if not request.user.is_authenticated:
        return render(request, 'accounts/profile.html', {'guest': True})

    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi.')
            return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
