from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.shortcuts import render
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from .models import *
from challenge.models import *
from rest_framework import status
from .utils import *


class MonthViewset(ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer


class DiaryViewset(ModelViewSet):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer

    # complete diary
    @action(detail=True, methods=['patch'])
    def finish_diary(self, request, pk=None):
        diary = get_object_or_404(Diary, id=pk)
        qandas = QandA.objects.filter(diary_id=diary.id)

        # qanda가 하나라도 존재하는 경우 (성공)
        if qandas.exists(): 
            try:
                result = complete_diary(pk)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # QandA 객체가 없으면 홈 화면으로 리다이렉트
        else:
            months = Month.objects.filter(user_id=diary.user_id)
            serializer = MonthSerializer(months, many=True)
            return Response({
                "status": "redirect",
                "data": serializer.data,
                "message": "No QandA found. Redirecting to home screen."
            }, status=status.HTTP_200_OK)

    # 현재, 이전, 다음 다이어리 조회
    @action(detail=True, methods=['get'])
    def view_diary(self, request, pk=None):
        try:
            diary = get_object_or_404(Diary, id=pk)
            diary_context = get_diary_context(diary)
            return Response({"status": "success", "data": diary_context}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # diary list 불러오기 (월 폴더 선택 시)
    @action(detail=False, methods=['get'], url_path='list_diaries')
    def list_diaries(self, request, month_id=None):
        month_id = request.query_params.get('month_id')
        if not month_id:
            return Response({"status": "error", "message": "month_id is required"}, status=400)
        
        queryset = self.queryset.filter(month_id=month_id, is_complete=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})


class QandAViewset(ModelViewSet):
    queryset = QandA.objects.all()
    serializer_class = QandASerializer

    def create(self, request, *args, **kwargs):
        try:
            diary_id = request.data.get('diary_id')
            answer = request.data.get('answer')
            if not diary_id or not answer:
                return Response({
                    "status": "error",
                    "message": "diary_id and answer are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            diary = get_object_or_404(Diary, id=diary_id)
            qanda = QandA.objects.create(diary_id=diary, answer=answer)

            followup_question = get_followup_question(answer)
            qanda.question = followup_question
            qanda.save()

            # 다이어리가 완료되었는지 확인 (complete_diary 함수 호출)
            if QandA.objects.filter(diary_id=diary.id).count() == diary.limitq_num:
                complete_diary(diary_id)

            return Response({
                "status": "success",
                "data": QandASerializer(qanda).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)