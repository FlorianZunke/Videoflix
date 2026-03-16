import os
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.contrib.staticfiles import finders
from functools import lru_cache

def get_logo_data():
    """
    Helper function to load the logo image data for email attachments.
    """
    path = os.path.join(settings.BASE_DIR, 'static', 'videoflix', 'images', 'logo_icon.svg')
    
    if not os.path.exists(path):
        return None
        
    with open(path, 'rb') as f:
        image_data = f.read()
    
    logo = MIMEImage(image_data, _subtype="svg+xml")
    logo.add_header('Content-ID', '<logo>')
    return logo

def job_send_activation_mail(recipient_email, activation_link):
    """
    Sends an activation email to the user with the provided activation link.
    """
    subject = "Aktiviere dein Videoflix Konto"
    context = {'email': recipient_email, 'link': activation_link}
    
    html_message = render_to_string('activation_mail.html', context)
    plain_message = strip_tags(html_message)
    
    msg = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email]
    )
    msg.attach_alternative(html_message, "text/html")
    
    logo = get_logo_data()
    if logo:
        msg.attach(logo)
    
    msg.send(fail_silently=False)


def job_send_reset_password_mail(recipient_email, reset_link):
    """
    Sends a password reset email to the user with the provided reset link.
    """
    subject = "Passwort zurücksetzen für dein Videoflix Konto"
    context = {'email': recipient_email, 'link': reset_link}
    
    html_message = render_to_string('reset_password.html', context)
    plain_message = strip_tags(html_message)
    
    msg = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email]
    )
    msg.attach_alternative(html_message, "text/html")
    
    logo = get_logo_data()
    if logo:
        msg.attach(logo)
    
    msg.send(fail_silently=False)