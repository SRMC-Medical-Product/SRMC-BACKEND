from calendar import c
from urllib import request
from rest_framework.serializers import ModelSerializer
from .models import *

class DoctorTimingsSerializer(ModelSerializer):

    class Meta:
        model=DoctorTimings
        fields="__all__"

class DoctorScheduleSerializer(ModelSerializer):

    class Meta:
        model=DoctorSchedule
        fields="__all__"

class CategorySpecialistSerializer(ModelSerializer):
	class Meta:
		model =CategorySpecialist
		fields='__all__'

	def __init__(self, *args, **kwargs):
		super(CategorySpecialistSerializer, self).__init__(*args, **kwargs) 
		request = self.context.get('request')
		if request and request.method == 'POST':
			self.Meta.depth = 0
		elif request and request.method == 'PUT':
			self.Meta.depth = 0 
		else:
			self.Meta.depth = 4
class DepartmentSerializer(ModelSerializer):
	class Meta:
		model = Department
		fields='__all__'


class DoctorSerializer(ModelSerializer):
	class Meta:
		model = Doctor
		fields='__all__'
	
	def __init__(self,*args,**kwargs):
		super(DoctorSerializer,self).__init__(*args,**kwargs)
		request=self.context.get('request')
		if request and request.method=='POST' :
			self.Meta.depth = 0
		elif request and request.method=='PUT':
				self.Meta.depth = 0 
		else:
			self.Meta.depth = 3
