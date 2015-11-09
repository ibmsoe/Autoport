__author__ = 'yuehaitao'
from django.conf import settings
from django.core.mail import EmailMessage

EMAIL_HOST_USER = getattr(settings, 'EMAIL_HOST_USER', '')


def send_html_email(subject, html_content, recipient_list):
    msg = EmailMessage(subject, html_content, EMAIL_HOST_USER, recipient_list)
    msg.content_subtype = "html"
    try:
        msg.send(fail_silently=False)
    except Exception:
        raise Exception
