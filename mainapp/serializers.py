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