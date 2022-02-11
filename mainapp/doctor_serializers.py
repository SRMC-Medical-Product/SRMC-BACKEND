from rest_framework.serializers import ModelSerializer
from .models import *

class DoctorTimingsSerializer(ModelSerializer):

    class Meta:
        model=DoctorTimings
        fields="__all__"

class CategorySpecialistSerializer(ModelSerializer):
	class Meta:
		model =CategorySpecialist
		fields='__all__'

class DepartmentSerializer(ModelSerializer):
	class Meta:
		model = Department
		fields='__all__'