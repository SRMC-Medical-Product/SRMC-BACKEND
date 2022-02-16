'''Django imports'''
from django.contrib.auth import authenticate 
from django.db.models import Q
from django.conf import settings
from datetime import datetime as dtt , time , timedelta

'''imports'''
import uuid 
import math 
from urllib.parse import urlparse , parse_qs

#TODO : using admin auth by default
'''Authentication Permission'''
from adminapp.authentication import AdminAuthentication

'''Model Import'''
from .models import *
from mainapp.models import * 

'''Serializer Import'''
from mainapp.support_serializers import *
from mainapp.serializers import *
from mainapp.doctor_serializers import *

'''Response Import'''
from myproject.responsecode import display_response,exceptiontype,exceptionmsg

'''Rest Framework'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


'''Time Format Imports'''
from myproject.datetimeformat import HMSf, dmY,Ymd,IMp,YmdHMS,dmYHMS,YmdTHMSf,YmdHMSf,HMS

'''department''' 
class DepartmentsView(APIView):

    # authentication_classes = [AdminAuthentication]
    # permission_classes = [SuperAdminPermission]
    
    '''Get All Departments'''
    def get(self , request, format=None):
        ACTION = "Departments GET"
        snippet = Department.objects.all()
        print(snippet)
        if snippet is None:
            return display_response(
            msg = ACTION,
            err= "No data found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = DepartmentSerializer(snippet,many=True,context={'request' :request}) 
        json_data = []
        for i in serializer.data:
            json_data.append({
                "id":i["id"],
                "name":i["name"],
                "img":i["img"],
                "head":i["head"],
                "enable" : i['enable']
            })
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

'''specilization view'''
'''
    json_data : [
        {
            "id":"id",
            "name":"name",
            "img":"img",
            "departments" : [
                {
                    "id":"id",
                    "name":"name",
                    "img":"img",
                    "head":"head",
                    "enable" : "enable"
                }
            ]
        },
    ]
'''
class SpecializationInDetail(APIView):

    def  get(self , request , format=None):
        ACTION = "SpecializationInDetail GET"
        snippet = CategorySpecialist.objects.all()
        serializer = CategorySpecialistSerializer(snippet,many=True,context={'request' :request}) 

        json_data = []
        for i in serializer.data :
            data = {
                "id" : i['id'],
                "name" : i['name'], 
                "img" : i['img'],  
                "departments" : []
            }
    
            for j in i['depts'] :
                data['departments'].append({
                    "id" : j['id'],
                    "name" : j['name'],
                    "img" : j['img'],
                    "head" : j['head'],
                    "enable" : j['enable']
                })
                
            json_data.append(data)
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

''' appointments history'''

"""
    json_data :[ 
        {
        "id" : "id",
        "patient" : {
                    "id" : "id",
                    "name" : "name",
                },
        "doctor" : {
                    "id" : "id",
                    "name" : "name",
                    "profile_img" : "profile_img",
                },
        "date" : "date",
        "time" : "time",
        "timeline" : {
                "step1":{
                    "title" : "Booking Confirmed",
                    "time" : "IMP format",
                    "completed" : bool
                },
                "step2":{
                    "title" : "Arrived at Hospital",
                    "time" : "IMP format",
                    "completed" : bool
                },
                "step3":{
                    "title" : "Consulted",
                    "time" : "IMP format",
                    "completed" : bool
                },
            },
        },
    ]
"""

class AppointmentsHistory(APIView):
    # authentication_classes = [AdminAuthentication] 
    # permission_classes = [SuperAdminPermission]

    def get(self , request , format=None):
        ACTION = "AppointmentsHistory GET"
        snippet = Appointment.objects.all().order_by('date')
        serializer = AppointmentSerializer(snippet,many=True,context={'request' :request})
        json_data = [] 
        for i in serializer.data :
            json_data.append({
                "id" : i['id'],
                "patient" : patient_data,
                "doctor" : doctor_data,
                "date" : i['date'],
                "time" : i['time'],
                "timeline" : i['timeline'],
            })


            for j in i['patient'] :
                patient_data = {
                    "id" : j['id'],
                    "name" : j['name'],
                }
            
            for k in i['doctor'] : 
                doctor_data = {
                    "id" : k['id'],
                    "name" : k['name'],
                    "profile_img" : k['profile_img'],
                }
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )
                    
''' doctor get '''                    
class DoctorGet(APIView):
    # authentication_classes = [AdminAuthentication] 
    # permission_classes = [SuperAdminPermission]

    def get(self , request , format=None):
        ACTION = "Doctor GET"
        snippet = Doctor.objects.all() 
        serializer = DoctorSerializer(snippet,many=True,context={'request' :request})
        json_data = []
        for i in serializer.data :
            json_data.append([{
                "id" : i['id'],
                "doctor_id" : i['doctor_id'], 
                "name" : i['name'],
                "profile_img" : i['profile_img'],
                "specialisation" : i['specialisation'],
                "is_blocked" : i['is_blocked'],
            }]) 
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

''' single doctor details get'''
class DoctorDetails(APIView): 
    # authentication_classes = [AdminAuthentication] 
    # permission_classes = [SuperAdminPermission]

    def get(self , request , format=None):
        ACTION = "DoctorDetails GET"
        id = request.query_params.get('id')

        json_data = {
            "details" : {},
            "timings" : {},
            "schedule" : {},
            "appointments" : {}
        }
        if id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        snippet = Doctor.objects.filter(id=id).first()
        serializer = DoctorSerializer(snippet,context={'request' :request})
        
        '''Details'''
        json_data['details'] = serializer.data
        timings = DoctorTimings.objects.filter(doctor_id__id=id).first()
        
        '''Timings'''
        timings_serializer = DoctorTimingsSerializer(timings,context={'request' :request})
        json_data['timings'] = timings_serializer.data 
        
        '''Schedule'''
        schedule = DoctorSchedule.objects.filter(doctor_id__id=id).first()
        schedule_serializer = DoctorScheduleSerializer(schedule,context={'request' :request})
        json_data['schedule'] = schedule_serializer.data

        return display_response(
            msg = ACTION,
            err= None, 
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

'''patient get'''
class PatientGet(APIView):
    # authentication_classes = [AdminAuthentication] 
    # permission_classes = [SuperAdminPermission]     
    def get(self , request , format=None):
        ACTION = "Patients GET"
        snippet = Patient.objects.all() 
        serializer = PatientSerializer(snippet,many=True,context={'request' :request})
        json_data = []
        for i in serializer.data :
            json_data.append([{
                "id" : i['id'],
                "name" : i['name'], 
                "email" : i['email'], 
                "blood" : i['blood'], 
                "gender" : i['gender'], 
            }]) 

        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )  

''' single patient details get'''
class PatientDetails(APIView):
    # authentication_classes = [AdminAuthentication]
    # permission_classes = [SuperAdminPermission] 
    def get(self , request , format=None):
        ACTION = "PatientDetails GET"
        id = request.query_params.get('id')

        json_data = {
            "details" : {},
            "appointments" : {}
        }
        ''' check id for null ''' 
        if id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        snippet = Patient.objects.filter(id=id).first()
        serializer = PatientSerializer(snippet,context={'request' :request})
        json_data["details"] = serializer.data
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

