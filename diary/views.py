from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.shortcuts import render
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from .models import *
from challenge.models import *
from rest_framework import status


def get_diary_context(diary):
    month = diary.month_id
    diaries = Diary.objects.filter(month_id=month).order_by('created_date')

    diary_list = list(diaries)
    diary_index = diary_list.index(diary)

    previous_diary = diary_list[diary_index - 1] if diary_index > 0 else None
    next_diary = diary_list[diary_index + 1] if diary_index < len(diary_list) - 1 else None

    previous_diary_serialized = DiarySerializer(previous_diary).data if previous_diary else None
    next_diary_serialized = DiarySerializer(next_diary).data if next_diary else None
    diary_serialized = DiarySerializer(diary).data

    return {
        "diary": diary_serialized,
        "previous_diary": previous_diary_serialized,
        "next_diary": next_diary_serialized,
    }

def complete_diary(diary_id):
    diary = get_object_or_404(Diary, id=diary_id)
    qandas = QandA.objects.filter(diary_id=diary.id)

    if qandas.exists():
        diary.is_complete = True
        diary.save()

        month_obj = diary.month_id
        if month_obj:
            month_obj.count += 1
            month_obj.save()

        daily_challenge = DailyChallenge.objects.filter(user_id=diary.user_id).first()
        if daily_challenge:
            daily_challenge.today_complete = True
            daily_challenge.current_day += 1
            daily_challenge.save()

            user = User.objects.get(id=diary.user_id.id)
            if not user.is_firstday:
                user.is_firstday = True
                user.save()

                Badge.objects.create(
                    title="1",
                    type="firstday",
                    user_id=user
                )

            if daily_challenge.current_day == daily_challenge.goal_day:
                goal_badge_exists = Badge.objects.filter(
                    title=str(daily_challenge.goal_day),
                    user_id=user
                ).exists()
                if not goal_badge_exists:
                    Badge.objects.create(
                        title=str(daily_challenge.goal_day),
                        type="goal_day",
                        user_id=user
                    )
                daily_challenge.current_day = daily_challenge.goal_day
                daily_challenge.goal_day += 7
                daily_challenge.save()

        all_daily_challenges = DailyChallenge.objects.all()
        for challenge in all_daily_challenges:
            if challenge.today_complete:
                challenge.today_complete = False
            else:
                challenge.current_day = 0
                challenge.goal_day = 7
            challenge.save()

        diary_context = get_diary_context(diary)
        return {"status": "success", "data": diary_context}

    return {"status": "error", "message": "Diary is not yet complete"}


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

    # diary list 불러오기 (월 폴더 선택 시)
    @action(detail=True, methods=['get'])
    def view_diary(self, request, pk=None):
        try:
            diary = get_object_or_404(Diary, id=pk)
            diary_context = get_diary_context(diary)

            return Response({"status": "success", "data": diary_context}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QandAViewset(ModelViewSet):
    queryset = QandA.objects.all()
    serializer_class = QandASerializer