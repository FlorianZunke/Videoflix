from django.core.mail import send_mail
from django.conf import settings

def job_send_activation_mail(recipient_email, activation_link):
    subject = "Aktiviere dein Videoflix Konto"
    message = f"Bitte aktiviere dein Konto, indem du auf diesen Link klickst: {activation_link}"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )