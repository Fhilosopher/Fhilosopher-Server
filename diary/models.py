from django.db import models
from accounts.models import User

class Month(models.Model):
    stamp = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    year = models.IntegerField()
    month = models.IntegerField()

    # date 필드에서 연도와 월을 추출하여 저장
    def save(self, *args, **kwargs):
        if self.date:
            self.year = self.date.year
            self.month = self.date.month
        super().save(*args, **kwargs)


class Diary(models.Model):
    first_q = models.TextField()
    limitq_num = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    month_id = models.ForeignKey(Month, on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.


class QandA(models.Model):
    answer = models.TextField()
    question = models.TextField()
    diary_id = models.ForeignKey(Diary, on_delete=models.CASCADE)

    def __str__(self):
        return self.answer

