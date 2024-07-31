from rest_framework import serializers
from .models import User
from challenge.models import DailyChallenge,Badge

#badge serializer
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

##dailychallenge serializer
class DailyChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyChallenge
        fields = '__all__'

#mypage
class MypageSerializer(serializers.ModelSerializer):
    Badges = BadgeSerializer(many=True)
    DailyChallenges = DailyChallengeSerializer()
    class Meta : 
        model = User
        fields= ['name','is_alert','alert_hour','alert_min','is_firstday','Badges','DailyChallenges']
