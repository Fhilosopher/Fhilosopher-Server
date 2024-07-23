from django.db import models
from accounts.models import User

class Month(models.Model):
    date = models.DateField(auto_now_add=True)
    year = models.IntegerField()
    month = models.IntegerField()
    count = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    # date 필드에서 연도와 월을 추출하여 저장
    def save(self, *args, **kwargs):
        if self.date:
            self.year = self.date.year
            self.month = self.date.month
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_id}의 {self.month}월 폴더 {self.count}개 일기 "


class Diary(models.Model):
    firstq = models.TextField()
    limitq_num = models.IntegerField(default=6)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    month_id = models.ForeignKey(Month, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_id}의 {self.created_date}일 일기 - {self.is_complete}"


class QandA(models.Model):
    answer = models.TextField()
    question = models.TextField(null=True, blank=True)
    diary_id = models.ForeignKey(Diary, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer

