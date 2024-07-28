import os
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from challenge.models import *
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError, APIConnectionError, RateLimitError, APIStatusError


load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def initialize_interviewer(firstq):
    system_prompt = {"role": "system", "content": "You are an interviewer who asks engaging follow-up questions based on the user's answers."}
    messages = [
        system_prompt,
        {"role": "assistant", "content": firstq}
    ]

    return messages

def get_followup_question(messages, answer):
    messages.append({"role": "user", "content": answer})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    follow_up_question = response.choices[0].message.content
    messages.append({"role": "assistant", "content": follow_up_question})
    return follow_up_question, messages


def get_diary_context(diary):
    month = diary.month_id
    diaries = Diary.objects.filter(month_id=month, is_complete=True).order_by('created_date')

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

    # 조건문 지워도 될것같음
    if qandas.exists():
        diary.is_complete = True
        diary.save()

        month_obj = diary.month_id
        if month_obj:
            month_obj.count += 1
            month_obj.save()

        daily_challenge = DailyChallenge.objects.filter(user_id=diary.user_id).first()
        print(daily_challenge)

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
                daily_challenge.start_day = daily_challenge.current_day
                daily_challenge.current_day = daily_challenge.goal_day
                daily_challenge.goal_day += 7
                daily_challenge.save()

        diary_context = get_diary_context(diary)
        return {"status": "success", "data": diary_context}

    return {"status": "error", "message": "Diary is not yet complete"}