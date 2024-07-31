from django.db import models


class FirstQuestion(models.Model):
    questions = models.JSONField()
