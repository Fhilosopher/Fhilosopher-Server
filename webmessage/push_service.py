import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import Subscription

def send_push_notification(subscription_info, message):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(message),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=settings.VAPID_CLAIMS
        )
    except WebPushException as ex:
        print("I'm sorry, Dave, but I can't do that: {}", repr(ex))

def trigger_push_notifications(title, body, icon):
    message = {
        'title': title,
        'body': body,
        'icon': icon
    }
    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        send_push_notification(subscription_info={
            'endpoint': subscription.endpoint,
            'keys': subscription.keys
        }, message=message)

# 기존 push_service.py 코드에 추가

def test_push_notification():
    title = "Test Notification"
    body = "This is a test notification"
    icon = "https://example.com/icon.png"

    trigger_push_notifications(title, body, icon)

# 스크립트로 실행 가능하게 추가
if __name__ == "__main__":
    test_push_notification()

