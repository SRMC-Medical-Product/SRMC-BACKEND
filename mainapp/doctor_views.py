"""
    File with all the API's relating to the doctor app
"""
from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


from .models import *
from .auth import *
from .serializers import *

class LoginDoctor(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,format=None):

        data=request.data

        userid=data.get("userid",None)
        pin=data.get("pin",None)

        if userid in [None,""] or pin in [None,""]:

            return Response({
                        "MSG":"FAILED",
                        "ERR":"Please provide userid and pin",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)

        doctor=Doctor.objects.filter(doctor_id=userid,pin=pin)

        if doctor.exists():
            doctor=doctor[0]
        else:
            
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Doctor does not exist",
                    "BODY":None
                        },status=status.HTTP_400_BAD_REQUEST)
        
        token=generate_token({
                "id":doctor.id
                    })

        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":{
                        "token":token
                            }
                        },status=status.HTTP_200_OK) 