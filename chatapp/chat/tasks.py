from celery import shared_task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_email_task(to_email):
    try:
        logger.info(f"Sending email to {to_email}...")
        send_mail(
            subject="Test Email",
            message="This is a test from Celery!",
            from_email="noreply@example.com",
            recipient_list=[to_email],
        )
        return "Email sent successfully"
    except Exception as e:
        logger.error(f"Email task failed: {e}")
        raise
