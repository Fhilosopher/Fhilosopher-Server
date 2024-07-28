from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyPageViewSet,KakaoLoginView

router = DefaultRouter()
router.register(r'MyPage', MyPageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('dj_rest_auth.urls')),
    path('', include('dj_rest_auth.registration.urls')),
    path('kakaoLogin/',KakaoLoginView.as_view(),name='KakaoLogin'),
]