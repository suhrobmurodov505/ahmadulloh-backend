from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """User modelini kengaytiruvchi qo'shimcha ma'lumotlar (telefon, manzil, rasm)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Telefon raqami', max_length=32, blank=True)
    address = models.CharField('Manzil', max_length=500, blank=True)
    avatar = models.ImageField('Profil rasmi', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profillar'

    def __str__(self):
        return f'{self.user.username} profili'
