from django.db import models
from accounts.models import User
from firstQuestion.models import FirstQuestion
from datetime import datetime, time, timedelta


class Month(models.Model):
    date = models.DateField(auto_now_add=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    count = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user_id}의 {self.month}월 폴더 {self.count}개 일기 "


class Diary(models.Model):
    firstq = models.TextField(null=True, blank=True)
    limitq_num = models.IntegerField(default=6)
    created_date = models.DateField(null=True, blank=True)
    created_time = models.TimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    messages = models.JSONField(default=list)  # 대화 흐름을 저장하기 위한 필드
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    month_id = models.ForeignKey(Month, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.created_date:
            now = datetime.now()
            if now.time() <= time(5, 0):
                self.created_date = (now - timedelta(days=1)).date()
            else:
                self.created_date = now.date()

        if not self.firstq:  # firstq가 비어 있을 때만 설정
            user = self.user_id
            firstq_index = user.firstq_index
            first_question = FirstQuestion.objects.first()
            
            if first_question and len(first_question.questions) > 0:
                questions = first_question.questions
                if 0 <= firstq_index < len(questions):
                    self.firstq = questions[firstq_index]
                    print(f"firstq set to: {self.firstq}")
                else:
                    print(f"Invalid index: {firstq_index}")
            else:
                print("FirstQuestion or questions not found")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id}의 {self.created_date}일 일기 - {self.is_complete}"


class QandA(models.Model):
    answer = models.TextField()
    question = models.TextField(null=True, blank=True)
    diary_id = models.ForeignKey(Diary, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer
