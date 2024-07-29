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
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
class MonthViewset(ModelViewSet):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # diary list 불러오기 (월 폴더 선택 시)
    @action(detail=False, methods=['get'], url_path='list_months')
    def list_months(self, request, user_id=None):
        user_id = int(request.query_params.get('user_id'))
        authenticated_user_id = request.user.id
        if not user_id:
            return Response({"status": "error", "message": "month_id is required"}, status=400)
        
        try:
            user_id = int(user_id)
        except ValueError:
            return Response({"status": "error", "message": "user_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_id != authenticated_user_id :
            return Response({"status": "error", "message": "훔쳐보지마~!"}, status=401)
        
        queryset = self.queryset.filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})


class DiaryViewset(ModelViewSet):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        created_date = timezone.now().date()

        # Check if a diary entry already exists for this user and date
        if Diary.objects.filter(user_id=user_id, created_date=created_date).exists():
            return Response({
                "status": "error",
                "message": "A diary entry for this date already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = super().create(request, *args, **kwargs)
        diary = Diary.objects.get(id=response.data['id'])
        firstq = diary.firstq

        # Initialize GPT interviewer and get the first question
        messages = initialize_interviewer(firstq)
        
        # Save the initial messages to the diary
        diary.messages = messages
        diary.save()

        return Response({
            "status": "success",
            "data": DiarySerializer(diary).data,
        }, status=status.HTTP_201_CREATED)


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
        
        try:
            month = Month.objects.get(id=month_id)
        except Month.DoesNotExist:
            return Response({"status": "error", "message": "Invalid month_id"}, status=status.HTTP_400_BAD_REQUEST)
        
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
            messages = diary.messages

            followup_question, updated_messages = get_followup_question(messages, answer)
            diary.messages = updated_messages
            diary.save()

            new_qanda = QandA.objects.create(diary_id=diary, answer=answer, question=followup_question)

            # 다이어리가 완료되었는지 확인 (complete_diary 함수 호출)
            if QandA.objects.filter(diary_id=diary.id).count() == diary.limitq_num:
                complete_diary(diary_id)

            return Response({
                "status": "success",
                "data": QandASerializer(new_qanda).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)