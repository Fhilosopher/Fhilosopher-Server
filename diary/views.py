from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from .models import *


class MonthViewset(ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer

    # month_list 불러오기 (홈 화면)
    # @action(detail=False, methods=['get'], url_path='diary/month/<int:user_id>')
    # def list_months(self, request, user_id=None):
    #     queryset = self.queryset.filter(user_id=user_id)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class DiaryViewset(ModelViewSet):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer

    # diary list 불러오기 (월 폴더 선택 시)
    @action(detail=False, methods=['get'])
    def list_diaries(self, request, month_id=None):
        month_id = request.query_params.get('month_id')
        queryset = self.queryset.filter(month_id=month_id, is_complete=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QandAViewset(ModelViewSet):
    queryset = QandA.objects.all()
    serializer_class = QandASerializer