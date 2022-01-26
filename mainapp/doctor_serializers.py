from rest_framework.serializers import ModelSerializer
from .models import *

class DoctorTimingsSerializer(ModelSerializer):

    class Meta:
        model=DoctorTimings
        fields="__all__"