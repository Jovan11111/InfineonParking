import threading
from django.core.mail import send_mail

def send_mail_async(subject, message, from_email, recipient_list):
    def _send():
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    threading.Thread(target=_send).start()
