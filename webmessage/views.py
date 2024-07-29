import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from .models import Subscription
from .webpush import send_web_push, send_push_to_all_subscribers

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        subscription = Subscription(
            endpoint=data['endpoint'],
            p256dh=data['keys']['p256dh'],
            auth=data['keys']['auth']
        )
        subscription.save()
        return JsonResponse({'message': 'Subscription saved.'})
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

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

@csrf_exempt
def send_push_to_all(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        title = data.get('title', 'BODA')
        message = data.get('message', 'This is a test push notification!')
        icon = data.get('icon')
        badge = data.get('badge')
        image = data.get('image')
        url = data.get('url')
        
        results = send_push_to_all_subscribers(title, message, icon, badge, image, url)
        return JsonResponse({'results': results})
    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def home(request):
    context = {
        'vapid_public_key': settings.VAPID_PUBLIC_KEY
    }
    return render(request, 'webmessage/index.html', context)
