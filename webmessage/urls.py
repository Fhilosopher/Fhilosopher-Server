from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('send_push/', views.send_push, name='send_push'),
    path('send_push_to_all/', views.send_push_to_all, name='send_push_to_all'),
    path('', views.home, name='home'),
]
