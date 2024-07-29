from django.db import models

class Subscription(models.Model):
    endpoint = models.TextField(null=True, blank=True)
    p256dh = models.TextField(null=True, blank=True)
    auth = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.endpoint
