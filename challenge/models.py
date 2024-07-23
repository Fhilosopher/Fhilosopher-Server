from django.db import models
from accounts.models import User


class DailyChallenge(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_day = models.IntegerField(default=0)
    goal_day = models.IntegerField(default=7)
    today_complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_id)

class Badge(models.Model):
    title = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title