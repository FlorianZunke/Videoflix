# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from django.core.mail import send_mail
# from django.conf import settings
# from django.contrib.auth import get_user_model
# import django_rq

# from .utils import job_send_activation_mail

# User = get_user_model()

# @receiver(post_save, sender=User)
# def send_activation_email(sender, instance, created, **kwargs):
#     if created and not instance.is_active:
#         uid = getattr(instance, 'activation_uid', '')
#         token = getattr(instance, 'activation_token', '')
        
#         activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
        
#         job_send_activation_mail(instance.email, activation_link)