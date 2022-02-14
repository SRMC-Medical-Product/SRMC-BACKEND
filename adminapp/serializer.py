from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

'''Admin Serializer'''
class AdminDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
