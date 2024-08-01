import json
# from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

# from webmessage.task import send_web_push
from .models import Subscription
# from .webpush import send_web_push, send_push_to_all_subscribers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .task import send_web_push

class SubscribeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        user = request.user  # JWT 토큰으로 인증된 사용자

        # Subscription 모델에 사용자 ID와 구독 정보를 저장
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            endpoint=data['endpoint'],
            defaults={
                'p256dh': data['keys']['p256dh'],
                'auth': data['keys']['auth'],
            }
        )

        if not created:
            # 기존 구독 정보가 있는 경우 업데이트
            subscription.p256dh = data['keys']['p256dh']
            subscription.auth = data['keys']['auth']
            subscription.save()

        return JsonResponse({'message': 'Subscription saved.'})

#웹푸시 테스트용. 실제 배포시 사용X
@csrf_exempt
def send_push(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        subscription_info = {
            "endpoint": data['endpoint'],
            "keys": {
                "p256dh": data['keys']['p256dh'],
                "auth": data['keys']['auth']
            }
        }
        title = data.get('title', 'BODA')
        message = data.get('message', 'This is a test push notification!')
        icon = data.get('icon')
        badge = data.get('badge')
        image = data.get('image')
        url = data.get('url')
        
        result = send_web_push(subscription_info, title, message, icon, badge, image, url)
        if result.get('status') == 500:
            return JsonResponse(result, status=500)
        return JsonResponse(result)
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

# @csrf_exempt
# def send_push_to_all(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'message': 'Invalid JSON'}, status=400)

#         title = data.get('title', 'BODA')
#         message = data.get('message', 'This is a test push notification!')
#         icon = data.get('icon')
#         badge = data.get('badge')
#         image = data.get('image')
#         url = data.get('url')
        
#         results = send_push_to_all_subscribers(title, message, icon, badge, image, url)
#         return JsonResponse({'results': results})
#     return JsonResponse({'message': 'Invalid request method.'}, status=400)

# def home(request):
#     context = {
#         'vapid_public_key': settings.VAPID_PUBLIC_KEY
#     }
#     return render(request, 'webmessage/index.html', context)
