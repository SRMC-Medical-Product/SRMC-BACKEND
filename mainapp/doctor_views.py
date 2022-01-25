"""
    File with all the API's relating to the doctor app
"""
from wsgiref.util import request_uri
from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


from .models import *
from .auth import *
from .serializers import *
from .utils import *

import json
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

class ModifyDoctorTimings(APIView):

    authentication_classes=[DoctorAuthentication]
    permission_classes=[]

    def post(self,request,format=None):
        
        data=request.data

        days=data.get("days",None)
        start_time=data.get("start_time",None)
        end_time=data.get("end_time",None)
        duration=data.get("duration",None)

        if days in [None,""]:
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Invalid day data",
                    "BODY":None
                        },status=status.HTTP_400_BAD_REQUEST)
        
        if start_time in [None,""] or end_time in [None,""]:
            return Response({
                        "MSG":"FAILED",
                        "ERROR":"Invalid time data",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
            
        if duration in [None,""]:
            return Response({
                        "MSG":"FAILED",
                        "ERROR":"Invalid duration",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
        
        days_int=[]

        for i in range(7):
            if days[i]:
                days_int.append(i)
        
        availability={}

        current_date=generate_current_date()  #imported from utils.py

        doctor_timings_instance=DoctorTimings.objects.filter(doctor_id=request.user)

        if doctor_timings_instance.exists():
            doctor_timings_instance=doctor_timings_instance[0]
            
            doctor_timings_instance.delete()
        availability={"days":[
                {
                    
                        "day":"monday",
                        "date":"",
                        "available":False,

                    
                },
                {
                    
                        "day":"tuesay",
                        "date":"",
                        "available":False
                    
                },
                {
                   
                       "day":"wednesday",
                        "date":"",
                        "available":False
                    
                },
                {
                    
                        "day":"thursday",
                        "date":"",
                        "available":False
                    
                },
                {
                    
                        "day":"friday",
                        "date":"",
                        "available":False
                    
                },
                {
                    
                        "day":"saturday",
                        "date":"",
                        "available":False
                    
                },
                {
                    
                        "day":"sunday",
                        "date":"",
                        "available":False
                    
                },
            ]}     

        start_time=return_time_type(start_time)
        end_time=return_time_type(end_time)

        availability=update_availabilty(availability,current_date,days_int)

        doctor_timings_instance=DoctorTimings.objects.create(doctor_id=request.user,availability=availability,start_time=start_time,end_time=end_time,average_appoinment_duration=duration)
        
        return Response({
                "MSG":"SUCCESS",
                "ERR":None,
                "BODY":"Doctor Timings updated successfully"
                    },status=status.HTTP_200_OK)
                    