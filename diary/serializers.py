from rest_framework import serializers
from .models import Month, Diary, QandA


class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = "__all__"


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = "__all__"


class QandASerializer(serializers.ModelSerializer):
    class Meta:
        model = QandA
        fields = "__all__"
