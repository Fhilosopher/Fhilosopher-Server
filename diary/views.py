from django.shortcuts import render
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from .models import *


class MonthViewset(ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer


class DiaryViewset(ModelViewSet):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer


class QandAViewset(ModelViewSet):
    queryset = QandA.objects.all()
    serializer_class = QandASerializer