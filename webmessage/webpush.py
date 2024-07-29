import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import Subscription

def send_web_push(subscription_info, title, message, icon=None, badge=None, image=None, url=None):
    try:
        payload = json.dumps({
            "title": title,
            "body": message,
            "icon": icon,
            "badge": badge,
            "image": image,
            "url": url
        })

        webpush(
            subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=settings.VAPID_CLAIMS
        )
        return {'message': 'Push message sent successfully.'}
    except WebPushException as ex:
        return {'message': 'An error occurred: {}'.format(ex), 'status': 500}

def send_push_to_all_subscribers(title, message, icon=None, badge=None, image=None, url=None):
    subscriptions = Subscription.objects.all()
    results = []

    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth
            }
        }
        result = send_web_push(subscription_info, title, message, icon, badge, image, url)
        results.append(result)

    return results
