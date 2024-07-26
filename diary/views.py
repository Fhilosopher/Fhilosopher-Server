from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
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
    
    # 현재 다이어리와 이전, 다음 다이어리 불러오기
    @action(detail=True, methods=['get'])
    def view_diary(self, request, pk=None):
        diary = get_object_or_404(Diary, id=pk)
        month = diary.month_id
        diaries = Diary.objects.filter(month_id=month).order_by('created_date')

        # 현재 다이어리의 인덱스를 찾습니다.
        diary_list = list(diaries)
        diary_index = diary_list.index(diary)

        # 이전/다음 다이어리를 확인합니다.
        previous_diary = diary_list[diary_index - 1] if diary_index > 0 else None
        next_diary = diary_list[diary_index + 1] if diary_index < len(diary_list) - 1 else None

        previous_diary_serialized = DiarySerializer(previous_diary).data if previous_diary else None
        next_diary_serialized = DiarySerializer(next_diary).data if next_diary else None
        diary_serialized = DiarySerializer(diary).data

        context = {
            'diary': diary_serialized,
            'previous_diary': previous_diary_serialized,
            'next_diary': next_diary_serialized,
        }

        return Response(context)


class QandAViewset(ModelViewSet):
    queryset = QandA.objects.all()
    serializer_class = QandASerializer