# import os
# from celery import Celery
# from celery.schedules import crontab





# @app.task(bind=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")

# app.conf.beat_schedule ={
#     "test-add-numbers-every-10-seconds":{
#         "task": "chat.tasks.add_numbers",
#         "schedule": 50.0, 
#         "args":(),
#     }
# }

import os 
import logging
import requests
from celery import Celery, shared_task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')
app = Celery("chatapp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = get_task_logger(__name__)

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK") 
ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "you@example.com")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreplyexample.com")

def notify_failure_via_slack(task_name, task_id, exc, args, kwargs):
    if not SLACK_WEBHOOK:
        logger.warning("No SLACK_WEBHOOK set, skipping Slack alert")
        return
    text = f":rotating_lightt: Task *{task_name}* failed.\nID: `{task_id}`\nException: `{exc}`\nargs: `{args}`\nargs: `{kwargs}`"
    try:
        requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=5)
    except Exception as e:
        logger.exception("Failed to post Slack alert: %s", e)

def notify_failure_via_email(subject, message):
    try:
        send_mail(subject, message, FROM_EMAIL, [ALERT_EMAIL])
    except Exception as e:
        logger.exception("failed to send alert email: %s", e)


    @shared_task(
        bind=True,
        autoretry_for=(Exception,),
        retry_backoff_max=600,
        max_retries=5,
        acks_late=True
    )    

    def send_email_task(self, to_email):
        try:
            logger.warning("Sending email to %s...", to_email)
            return "Done"
        except Exception as exc:
            notify_failure_via_slack(self.name, self.request.id, str(exc), self.request.args, self.request.kwargs)
            notify_failure_via_email(
                subject=f"Task failure: {self.name}",
                message=f"Task {self.name} ({self.request.id}) failed with: {exc}\nargs={self.request.args}\nkwargs={self.request.kwargs}"
            )
            raise