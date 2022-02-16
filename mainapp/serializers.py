from rest_framework.serializers import ModelSerializer
from .models import *

class UserSerializer(ModelSerializer):
	class Meta:
		model=User
		fields='__all__'

class PromotionalSliderSerializer(ModelSerializer):
	class Meta:
		model = PromotionalSlider
		fields='__all__'

class CarouselSerializer(ModelSerializer):
	class Meta:
		model = Carousel
		fields='__all__'


class PatientNotificationSerializer(ModelSerializer):
	class Meta:
		model = PatientNotification
		fields='__all__'

class PatientSerializer(ModelSerializer):
	class Meta:
		model = Patient
		fields='__all__'

class CategoryPromotionSerializer(ModelSerializer):
	class Meta:
		model = CategoryPromotion
		fields='__all__'

class AppointmentSerializer(ModelSerializer):
	class Meta:
		model = Appointment
		fields='__all__'
	
	def __init__(self, *args, **kwargs):
		super(AppointmentSerializer, self).__init__(*args, **kwargs) 
		request = self.context.get('request')
		if request and request.method == 'POST':
			self.Meta.depth = 0
		elif request and request.method == 'PUT':
			self.Meta.depth = 0 
		else:
			self.Meta.depth = 4		

class HelpDeskUserSerializer(ModelSerializer):
	class Meta:
		model = HelpDeskUser
		fields='__all__'

	def __init__(self, *args, **kwargs):
		super(AppointmentSerializer, self).__init__(*args, **kwargs) 
		request = self.context.get('request')
		if request and request.method == 'POST':
			self.Meta.depth = 0
		elif request and request.method == 'PUT':
			self.Meta.depth = 0 
		else:
			self.Meta.depth = 4	