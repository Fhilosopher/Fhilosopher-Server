from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('send_push/', views.send_push, name='send_push'), #웹푸시 테스트용.실제배포시 사용X
    # path('send_push_to_all/', views.send_push_to_all, name='send_push_to_all'),
    # path('', views.home, name='home'),
]
