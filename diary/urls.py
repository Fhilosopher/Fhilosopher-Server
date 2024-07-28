from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'month', MonthViewset)
router.register(r'diary', DiaryViewset)
router.register(r'qna', QandAViewset)

urlpatterns = [
    path('', include(router.urls)),
]