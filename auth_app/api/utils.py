from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def job_send_activation_mail(recipient_username, activation_link):
    subject = "Aktiviere dein Videoflix Konto"
    context = {'username': recipient_username, 'link': activation_link}
    html_message = render_to_string('activation_mail.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_username],
        fail_silently=False,
        html_message=html_message
    )