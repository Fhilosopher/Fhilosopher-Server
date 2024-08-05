#일정시간마다 작동할 task. diary/scheduler에서 스케쥴
from datetime import datetime
import json
import pytz
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
    except Exception as e:
        print(f'General exception occurred: {e}')
        return {'message': 'An error occurred: {}'.format(e), 'status': 500}

def send_scheduled_notifications():
    # 현재 시간 구하기
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # 모든 구독 정보 확인
    subscriptions = Subscription.objects.all()

    for subscription in subscriptions:
        print(subscription.user)
        user = subscription.user
        print(f'hour:{user.alert_hour}')
        print(f'min:{user.alert_min}')
        # 유저의 알림 설정이 활성화되어 있고 현재 시간이 유저가 설정한 알림 시간인지 확인
        if user.is_alert:
            print(f'Checking alert for user {user}')
            if int(user.alert_hour) == current_hour and int(user.alert_min) == current_minute:
                send_web_push(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth
                        }
                    },
                    title="BODA",
                    message="BODA에 접속해서 답변을 남겨주세요~",
                    # icon="http://127.0.0.1:8000/static/penguin.jpg",
                    # badge="http://127.0.0.1:8000/static/penguin.jpg",
                    # image="http://127.0.0.1:8000/static/penguin.jpg",
                    url="https://bodaessay.vercel.app/"
                )


# def send_push_to_all_subscribers(title, message, icon=None, badge=None, image=None, url=None):
#     subscriptions = Subscription.objects.all()
#     results = []

#     for subscription in subscriptions:
#         subscription_info = {
#             "endpoint": subscription.endpoint,
#             "keys": {
#                 "p256dh": subscription.p256dh,
#                 "auth": subscription.auth
#             }
#         }
#         result = send_web_push(subscription_info, title, message, icon, badge, image, url)
#         results.append(result)

#     return results
