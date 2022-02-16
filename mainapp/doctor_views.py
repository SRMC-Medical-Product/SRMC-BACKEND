"""
    File with all the API's relating to the doctor app
"""
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime as dtt,time,date,timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


from .models import *
from .auth import *
from .doctor_serializers import *
from .utils import *
#from .utils import dmY,Ymd,IMp,HMS,YmdHMS,dmYHMS,YmdTHMSf,YmdHMSf,mdY,IST_TIMEZONE,YmdTHMSfz

class LoginDoctor(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,format=None):

        data=request.data

        
        userid=data.get("userid",None) #Both USERID and EMail are accepted
        pin=data.get("pin",None)

        if userid in [None,""] or pin in [None,""]:
            return Response({
                        "MSG":"FAILED",
                        "ERR":"Please provide userid and pin",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)


        """
            First we are checking with the userid and the pin.If the object instance is None then
            we will be checking the pin with the email.If the object instance is None then user credentials are wrong.
        """

        doctor=Doctor.objects.filter(doctor_id=userid,pin=pin)
        if doctor is None:
            doctor=Doctor.objects.filter(email=userid,pin=pin)

        if doctor.exists():
            doctor=doctor[0]
        else:
            
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Doctor does not exist",
                    "BODY":None
                        },status=status.HTTP_400_BAD_REQUEST)
        
        if doctor.is_blocked == False:
            token=generate_token({
                    "id":doctor.id
                        })

            """
                Setup the doctor activity
            """
            activity = DoctorActivity.objects.get_or_create(doctor_id=doctor)[0]
            now = dtt.now(IST_TIMEZONE)
            data = {
                "date" : now.strftime(dmY),
                "time" : now.strftime(HMS),
            }
            if len(activity.login) == 0:
                activity.login = [data]
            else:
                activity.login.append(data)
            activity.save()
            return Response({
                        "MSG":"SUCCESS",
                        "ERR":None,
                        "BODY":{
                            "token":token
                                }
                            },status=status.HTTP_200_OK) 
        else:
            return Response({
                "MSG":"FAILURE",
                "ERR":"You have been blocked by admin. Contact admin for more details",
                "BODY":None
                    },status=status.HTTP_401_UNAUTHORIZED) 
        
class ModifyDoctorTimings(APIView):
    """
        
        Doctor Profile Timings mofdify and create APIView
        Allowed methods:
            -POST
        
        Request data:
            days:       [boolean array,required] array of boolean data with each index maping to a specific day of the week with True reperesenting avaialble and False reperesenting not available
            start_time: [string time in isoformat(HH:MM:SS),required] start_time representing the time from which appoinments can begin
            end_time :  [string time in isoformat(HH:MM:SS),requires]   end_time representing the time after which no appoinments should be scheduled
            duration :  [Int,required] value representing the averation time duration of how long an appoinment can go
    
    """
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
        
       

        current_date=generate_current_date()  #imported from utils.py
        start_time=return_time_type(start_time)
        end_time=return_time_type(end_time)

        if start_time>=end_time:
            return Response({
                        "MSG":"FAILED",
                        "ERR":"Invalid time's given",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
        
        doctor_timings_instance=DoctorTimings.objects.filter(doctor_id=request.user)
        id=None
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
        time_slots=None
        if doctor_timings_instance.exists():
            doctor_timings_instance=doctor_timings_instance[0]
            id=doctor_timings_instance.id
            if doctor_timings_instance.availability:
                availability=doctor_timings_instance.availability
            if doctor_timings_instance.timeslots!={}:
                time_slots=doctor_timings_instance.timeslots
            #doctor_timings_instance.delete()
        
        #availabilty : json representing the availablity of the doctor for the week
             

        

        availability=update_availabilty(availability,current_date,days_int)
        time_slots=calculate_time_slots(start_time,end_time,duration,availability,time_slots=time_slots)
        if id==None:
            doctor_timings_instance=DoctorTimings.objects.create(doctor_id=request.user,availability=availability,start_time=start_time,end_time=end_time,average_appoinment_duration=duration,timeslots=time_slots)
        else:
            doctor_timings_instance.availability=availability
            doctor_timings_instance.start_time=start_time
            doctor_timings_instance.end_time=end_time
            doctor_timings_instance.average_appoinment_duration=duration
            doctor_timings_instance.timeslots=time_slots
            doctor_timings_instance.save()

            #doctor_timings_instance=DoctorTimings.objects.create(id=id,doctor_id=request.user,availability=availability,start_time=start_time,end_time=end_time,average_appoinment_duration=duration,timeslots=time_slots)
        return Response({
                "MSG":"SUCCESS",
                "ERR":None,
                "BODY":"Doctor Timings updated successfully"
                    },status=status.HTTP_200_OK)

class GetDoctorTimingsInProfile(APIView):

    authentication_classes=[DoctorAuthentication]
    permission_classes=[]

    def get(self,request,format=None):

        doctor_timings_instance=DoctorTimings.objects.filter(doctor_id=request.user)

        if doctor_timings_instance.exists():
            doctor_timings_instance=doctor_timings_instance[0]
        else:
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Create you timings",
                    "BODY":None
                        },status=status.HTTP_404_NOT_FOUND)

        doctor_timings_serializer=DoctorTimingsSerializer(doctor_timings_instance).data
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":doctor_timings_serializer
                        },status=status.HTTP_200_OK)