"""
    File with all the API's relating to the help desk user web
"""
from tkinter.messagebox import NO
from unicodedata import name
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime as dtt,time,date,timedelta

from rest_framework.views import APIView
from rest_framework import status
# Create your views here.

from .models import *
from .auth import *
from .utils import *

'''encrypt'''
import hashlib 

'''Response Import'''
from myproject.responsecode import display_response,exceptiontype,exceptionmsg

'''Serializer Import'''
from .support_serializers import *
from mainapp.serializers import *
from mainapp.doctor_serializers import *

class LoginUser(APIView):
    authentication_classes = []
    permission_classes = []

    #TODO : Pin code encryption 
    
    def post(self,request,format=None):
        data = request.data
        userid = data.get("userid", None)  # Both USERID and EMail are accepted
        pin = data.get("pin", None)
        print(userid,pin)
        if userid in [None,""] or pin in [None,""]:
            return display_response(
                msg="FAILED",
                err="Please provide userid and pin",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        """
            First we are checking with the userid and the pin.If the object instance is None then
            we will be checking the pin with the email.If the object instance is None then user credentials are wrong.
        """

        user=HelpDeskUser.objects.filter(id=userid,pin=pin)
        if user is None:
            user=HelpDeskUser.objects.filter(email=userid,pin=pin)
        print(user) 
        if user.exists():
            user=user[0]
        else:
            return display_response(
                msg="FAILED",
                err="User does not exist",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_blocked == False:
            token=generate_token({
                "id":user.id,
            })
        
            """
                Setup the login activity
            """
            now = dtt.now(IST_TIMEZONE)
            logindata = {
                "date":now.strftime(dmY),
                "time":now.strftime(HMS),
            }
            if user.activity is None:
                formatdata = {
                    "login" :[]
                }
                formatdata["login"].append(logindata)
                user.activity = formatdata
            else:
                user.activity["login"].append(logindata)

            user.save()
            return display_response(
                msg="SUCCESS",
                err=None,
                body={
                    "token":token
                },
                statuscode=status.HTTP_200_OK
            )
        else:
            return display_response(
                msg="FAILED",
                err="User is blocked by the admin. Contact the administrator",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            ) 

'''department''' 
class DepartmentsView(APIView):

    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []
    
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

    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

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
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []

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
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []

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
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []

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
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []     

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
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []
     
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

''' get activity log for each support user'''
# todo : activity json_field
class ActivityLog(APIView):
    # authentication_classes = []
    # permission_classes = []  

    def get(self , request , format=None):
        ACTION = "ActivityLog GET"
        data = request.user 
        
        if data.id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Support User was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        
        get_user = HelpDeskUser.objects.filter(user_id=data.id).first()
        serializer = HelpDeskUserSerializer(get_user,context={'request' :request}) 
        
        data = serializer.data
        json_data = {
            "id" : data.id, 
            "name" : data.name,
            "activity" : data.activity
        }

        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

''' update user data ''' 

class UserData(APIView):  
    authentication_classes = []
    permission_classes = []

    def get(self , request , format=None):
        ACTION = "UserData GET" 
        data = request.user
        if data.id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Support User was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        get_user = HelpDeskUser.objects.filter(id=data.id).first()  
        serializer = HelpDeskUserSerializer(get_user,context={'request' :request})
        data = serializer.data
        json_data = {
            "id" : data.id,
            "name" : data.name,
            "email" : data.email,
            "mobile" : data.mobile,
            "counterno" : data.counterno,
            "pin" : data.pin,
            "is_blocked" : data.is_blocked,
            "specialisation" : [],
        }

        for i in data.specialisation : 
            json_data['specialisation'].append([{
                "id" : i.id,
                "name" : i.name
                }]) 
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

    def put(self , request , format=None):
        ACTION = "UserData PUT"
        data = request.data 
        id = data.get('id') 
        name = data.get('name') 
        email = data.get('email')  

        if id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Support User ID was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        get_user = HelpDeskUser.objects.filter(id=id).first()
        if name not in [None , ""]:
            get_user.name = name
            get_user.save()
        
        if email not in [None , ""]:
            get_user.email = email
            get_user.save()
        
        return display_response(
            msg = ACTION,
            err= None,
            body = None,
            statuscode = status.HTTP_200_OK
        ) 

class UserPinModify(APIView): 
    authentication_classes = []
    permission_classes = [] 

    def put(self , request, format= None): 
        ACTION = "UserPinModify PUT" 
        data = request.data
        id = data.get('id')
        pin = data.get('pin') 

        ''' check id for null ''' 
        if id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Support User ID was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        '''get user''' 
        get_user = HelpDeskUser.objects.filter(id=id).first()
        if pin not in [None , ""]:
            '''encrypt pin and save'''
            encryptpin = hashlib.sha256(str(pin).encode('utf-8')).hexdigest()
            get_user.pin = encryptpin
            get_user.save()

        return display_response(
            msg = ACTION,
            err= None,
            body = "Pin Changed Successfully",
            statuscode = status.HTTP_200_OK
        )

#TODO : json bookings

class BookAppointments(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self , request , format=None):
        ACTION = "HelpDesk BookAppointments POST"
        data = request.data 
        department = data.get('department')
        date = data.get('date')
        count = data.get('count')
        bookings = data.get('bookings') 

        
        