#일정시간마다 작동할 task. diary/scheduler에서 스케쥴
from datetime import datetime
import json
import pytz
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import Subscription
from urllib.parse import urlparse
from datetime import datetime, timedelta

def generate_vapid_claims(audience):
    return {
        "aud": audience,
        "exp": int((datetime.now() + timedelta(hours=12)).timestamp()),  # Unix 타임스탬프로 변환
        "sub": "mailto:jmg0916789@gmail.com"
    }
def send_web_push(subscription_info, title, message, icon=None, badge=None, image=None, url=None):
    try:
        # 구독 엔드포인트에서 푸시 서비스 URL 추출
        endpoint = subscription_info["endpoint"]
        parsed_url = urlparse(endpoint)
        aud = f"{parsed_url.scheme}://{parsed_url.netloc}"

        payload = json.dumps({
            "title": title,
            "body": message,
            "icon": icon,
            "badge": badge,
            "image": image,
            "url": url
        })

        vapid_claims = generate_vapid_claims(aud)

        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=vapid_claims
        )
        print('Web push sent successfully')
        return {'message': 'Push message sent successfully.'}
        
    except WebPushException as ex:
        print(f'WebPushException occurred: {ex}')
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
        #print(subscription.user)
        user = subscription.user
        #print(f'hour:{user.alert_hour}')
        #print(f'min:{user.alert_min}')
        # 유저의 알림 설정이 활성화되어 있고 현재 시간이 유저가 설정한 알림 시간인지 확인
        if user.is_alert:
            #print(f'Checking alert for user {user}')
            if user.alert_hour == current_hour and user.alert_min == current_minute:
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
                    # url="https://www.naver.com/"
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
