from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        uid = getattr(instance, 'activation_uid', '')
        token = getattr(instance, 'activation_token', '')
        
        activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
        
        subject = "Aktiviere dein Videoflix Konto"
        message = f"Bitte aktiviere dein Konto: {activation_link}"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )

@receiver(post_save, sender=User)
def send_password_reset_email(sender, instance, created, **kwargs):
    if not created and hasattr(instance, 'password_reset_token'):
        uid = getattr(instance, 'password_reset_uid', '')
        token = getattr(instance, 'password_reset_token', '')
        
        reset_link = f"{settings.FRONTEND_URL}/reset-password-confirm/{uid}/{token}/"
        
        subject = "Passwort zurücksetzen für dein Videoflix Konto"
        message = f"Setze dein Passwort zurück: {reset_link}"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )