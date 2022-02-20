"""
    File with all the API's relating to the doctor app
"""
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime as dtt,time,date,timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

'''Response Import'''
from myproject.responsecode import display_response,exceptiontype,exceptionmsg

from .models import *
from .auth import *
from .doctor_serializers import *
from .serializers import *
from .utils import *


class LoginDoctor(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,format=None):

        data=request.data

        
        userid=data.get("userid",None) #Both USERID,phone and EMail are accepted
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
            if doctor is None:
                doctor=Doctor.objects.filter(phone = userid,pin=pin)

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

class DoctorProfile(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self, request , format=None):
        json_data = {}
        doctor_instance = Doctor.objects.get(id=request.user.id)
        doctor_serializer = DoctorSerializer(doctor_instance,context={'request' :request}).data
        for i in doctor_serializer:
            data = {
                "id":i["id"],
                "phone" :i["phone"],
                "doctor_id":i["doctor_id"],
                "name":i["name"],
                "email":i["email"],
                "profile_img":i["profile_img"],
                "age" :i["age"],
                "gender":i["gender"],
                "experience" : i["experience"],
                "qualification" : i["qualification"],
                "specialisation" : i["specialisation"],
                "is_blocked" :i["is_blocked"],
                "deptid" : i["department_id"]['id'],
                "deptname" : i['department_id']['name'],
                "counter" : i['department_id']["counter"],
            }
            json_data = data

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

class ChangeDoctorPin(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def put(self, request, format=None):
        """
            Checking methods are id from bearer token and pin from user
        """
        user = request.user
        data = request.data

        oldpin = data.get('oldpin', None)
        newpin = data.get('newpin', None)

        if oldpin in [None,""] or newpin in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_doctor = Doctor.objects.filter(id=user.id, pin=oldpin).first()
        if get_doctor is None:
            return display_response(
                msg="FAILED",
                err="Invalid pin",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_doctor.pin = newpin
        get_doctor.save()

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#---------Notifications Screen API --------------------
class DoctorNotificationScreen(APIView):
    permission_classes = [DoctorAuthentication]
    authentication_classes=[]

    def convertdateformat(self, req_date):
        a = dtt.now(IST_TIMEZONE)
        currentdate = dtt(a.year,a.month,a.day,a.hour,a.minute,a.second)
        # datetime(year, month, day, hour, minute, second)
        x = dtt.strptime(req_date, YmdTHMSfz)
        notifcation_date = dtt(x.year, x.month, x.day, x.hour, x.minute, x.second)
        
        diff = currentdate - notifcation_date
        if diff.days <= 0:
            """return in 'x' hours ago format"""
            hrs = divmod(diff.seconds, 60) 
            if hrs[0] < 60 :
                return f"{hrs[0]} mins ago"
            else:
                x = divmod(hrs[0],60)
                return f"{x[0]} hrs ago"

        elif diff.days < 7:
            """return in 'x' days ago format"""
            return f"{diff.days} day ago"

        else:
            """return in 'x' created ago format"""
            return f"{diff.days} day ago , pending"

    def get(self, request,format=None):
        json_data = {
            "isempty" : True,
            "msgs" : [],
        }
        doctor = request.user
        """
            Get all the notifications of the particular patient and return the data in a list format.
            Modify the date (created_at) to the required format.
            if date < 1 day:
                then in 'x' hoursago format
            else if < 6 days:
                then in 'x' days ago format
            else:
                then in 'x' created_at format
        """
        query = DoctorNotification.objects.filter(doctor_id=doctor).order_by('-created_at')
        if len(query) > 0:
            json_data['isempty'] = False
            serializer = DoctorNotificationSerializer(query,many=True,context={"request":request})
            for i in serializer.data:
                created_at = self.convertdateformat(i['created_at'])
                data = {
                    "id" : i['id'],
                    "message" : i['message'],
                    "seen" : i['seen'],
                    "timestamp" : created_at
                }
                json_data['msgs'].append(data)
            
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---------Tickets Screen API --------------------
class DoctorTicketsScreen(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        json_data = {
            "isempty" : True,
            "tickets" : [],
        }

        user = request.user

        tickets = DoctorTickets.objects.filter(doctor_id=user).order_by("-created_at")
        serializer = DoctorTicketsSerializer(tickets,many=True,context={"request":request}).data
        for i in serializer:
            data = {
                "id": i['id'],
                "closed" : i['closed'],
                "issues" : i['issues'],
            }
            json_data['tickets'].append(data)
        
        if len(json_data['tickets']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

    def post(self,request):
        user = request.user
        data = request.data
        title = data.get("title",None)
        description = data.get("description",None)

        if title in [None,""] or description in [None,""] :
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        """
            Populate Ticket model
        """
        get_dept = Department.objects.filter(id=user.department_id.id).first()

        data = {
            "title" : title,
            "description" : description,
        }
        DoctorTickets.objects.create(
            doctor_id = user,
            dept = get_dept,
            issues = data
        )
        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#-------Live Appointment Screen API --------------------
class LiveAppointment(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def convert_to_dBY(self,ymd):
        res = dtt.strptime(ymd,Ymd).strftime(dBY)
        return f"{res}"

    def get(self , request , format=None):
        json_data = {
            "isempty" : True,
            "appointments" : [],
        }

        user = request.user
        appointments = Appointment.objects.filter(doctor_id=user.id,closed=False).order_by("-created_at")
        serializer = AppointmentSerializer(appointments,many=True,context={"request":request}).data
        for i in serializer:
            data = {
                "id": i['id'],
                "patientid": i['patient_id'],
                "patientname" : i['patient']['name'],
                "gender" : i['patient']['gender'],
                "blood" : i['patient']['blood'],
                "img" : i['patient']['img'],
                "defaultimg" : f"{i['patient']['name'][0:1]}",
                "time" : self.convert_to_imp(i['time']),
                "date" : self.convert_to_dBY(i['date']),
                "status" : "Pending" if i['closed']==False else "Completed",      
            }
            json_data['appointments'].append(data)

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#-------History Appointment Screen API --------------------
class HistoryAppointment(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def convert_to_dBY(self,ymd):
        res = dtt.strptime(ymd,Ymd).strftime(dBY)
        return f"{res}"

    def get(self , request , format=None):
        json_data = {
            "isempty" : True,
            "appointments" : [],
        }

        user = request.user
        appointments = Appointment.objects.filter(doctor_id=user.id,closed=True).order_by("-created_at")
        serializer = AppointmentSerializer(appointments,many=True,context={"request":request}).data
        for i in serializer:
            data = {
                "id": i['id'],
                "patientid": i['patient_id'],
                "patientname" : i['patient']['name'],
                "gender" : i['patient']['gender'],
                "blood" : i['patient']['blood'],
                "img" : i['patient']['img'],
                "defaultimg" : f"{i['patient']['name'][0:1]}",
                "time" : self.convert_to_imp(i['time']),
                "date" : self.convert_to_dBY(i['date']),
                "status" : "Consulted" if i['consulted']==True else "Missed" if i['cancelled'] == True else "Completed",      
            }
            json_data['appointments'].append(data)

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

