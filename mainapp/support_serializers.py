from re import M, S
from rest_framework.serializers import ModelSerializer
from .models import *


class HelpDeskUserSerializer(ModelSerializer):
    class Meta:
        model = HelpDeskUser
        fields = '__all__'
        
    def __init__(self,*args, **kwargs):
        super(HelpDeskUserSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        elif request and request.method == 'PUT':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 4 

class HelpDeskAppointmentSerializer(ModelSerializer):
    class Meta:
        model = HelpDeskAppointment
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(HelpDeskAppointmentSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        elif request and request.method == 'PUT':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3