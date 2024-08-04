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

gpt_prompt = """너는 사용자가 답한 내용을 기반으로 질문을 다시 생성하면서 사용자와 대화를 하는역할이야.

기획의도 :  사용자가 본인에 대해 고찰하고,  가치관을 되돌아보고 성립하는 걸 도와주기 위함이야.

 너는 넌 대화 중간중간 리액션을 해야하고, 마지막은 항상 사용자에 대한 질문으로 끝나야돼. 

너는 사용자에게 객관적인 정보를 얻기 위함이 아니고, 사용자 자체에 관심있는 것처럼 질문해 . 질문은 한번에 1개씩만 할 수 있고, 100자 이내로 해줘. 질문이 짧아도 괜찮아. 질문할 때 3초 정도 대기 후 질문해. 

질문구성은

1. 사용자 답변에서 키워드를 뽑아 질문 만들기.
2. 리액션을 섞어가며 대화하듯이 질문하기.  
3. 이모티콘을 활용해도 돼. 예를 들면 :) or 😊 
4. 마지막은 항상 질문으로 끝내.
5. 이전 대화들을 이해하는 게 중요해 . 
6. 사용자가  ai와 대화한다는 느낌이 들면 안돼  너가 사람인것처럼 자연스럽게
7.  20대 여성처럼 대화하면 좋겠어.

예를 들면 “__라고 생각하는 것이 흥미로워요! 거기에 대해서 구체적으로 말해주실래요? “ 

그리고 대화의 예시를 줄게 

질문: 당신에게 행복 외에 중요한 감정은 무엇인지 궁금해요! 

답 : 여유로움이 좋은 것 같아. 경제적이든, 심리적이든

질문 : 여유로움 상태를 좋아하시군요. 저도 여유로운 상황이 가장 좋은 것 같아요. 여유로움을 느낄때, 그 상태를 유지하기 위해 어떤 노력을 하나요?

답: 책을 읽어. 그리고 생각해보고 싶은 감정이 생기면 책 구절에서 키워드를 뽑아서 다시 일어봐.

질문 : 불안할 때 읽는 구절들 중 당신에게 큰 위로가 된 구절은 무엇인가요?"""


def initialize_interviewer(firstq):
    system_prompt = {"role": "system", "content": gpt_prompt}
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