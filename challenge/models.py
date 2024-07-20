from django.db import models
from accounts.models import User


class DailyChallenge(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_day = models.IntegerField()
    goal_day = models.IntegerField()
    today_complete = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.user_id

class Badge(models.Model):
    title = models.CharField(max_length=50)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title