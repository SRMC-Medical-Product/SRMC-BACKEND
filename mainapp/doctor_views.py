"""
    File with all the API's relating to the doctor app
"""
from datetime import datetime as dtt,time,date,timedelta
import json
import uuid
from webbrowser import get

from html5lib import serialize

from myproject.responsecode import display_response,exceptiontype,exceptionmsg
from myproject.notifications import *

from .models import *
from .auth import *
from .doctor_serializers import *
from .serializers import *
from .utils import *
from .azurefunctions import *

from django.http import HttpResponse,FileResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class LoginDoctor(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,format=None):

        data=request.data

        
        userid=str(data.get("userid",None)) #Both USERID,phone and EMail are accepted
        pin=str(data.get("pin",None))

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

        doctor=Doctor.objects.filter(doctor_id=userid).first()
        if doctor is None:
            doctor=Doctor.objects.filter(email=userid).first()
            if doctor is None:
                doctor=Doctor.objects.filter(phone = userid).first()
        if doctor is None:            
            return Response({
                    "MSG":"FAILED",
                    "ERR":"User Id does not exist",
                    "BODY":None
                        },status=status.HTTP_400_BAD_REQUEST)
        
        """Checking Pin"""
        encrypted_doctor_pin=encrypt_doctor_pin(pin)
        if encrypted_doctor_pin != doctor.pin:
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Password is incorrect",
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
        doctor_instance = Doctor.objects.filter(id=request.user.id).first()
        doctor_serializer = DoctorSerializer(doctor_instance,context={'request' :request}).data
        i = doctor_serializer 
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
                statuscode=status.HTTP_404_NOT_FOUND
            )

        oldpin_encrypted_doctor_pin=encrypt_doctor_pin(oldpin)
      
        get_doctor = Doctor.objects.filter(id=user.id, pin=oldpin_encrypted_doctor_pin).first()
        if get_doctor is None:
            return display_response(
                msg="FAILED",
                err="Old pin is incorrect",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        newpin_encrypted_doctor_pin = encrypt_doctor_pin(newpin)

        get_doctor.pin = newpin_encrypted_doctor_pin
        get_doctor.save()

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#---------Notifications Screen API --------------------
class DoctorNotificationScreen(APIView):
    authentication_classes=[DoctorAuthentication]
    permission_classes = []

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

    def put(self , request):
        notificationid = request.data.get('notificationid', None)
        if notificationid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        doctor = request.user
        
        query = DoctorNotification.objects.filter(doctor_id__id=doctor.id,id=notificationid).first()
        if query is None:
            return display_response(
                msg="FAILED",
                err="Invalid data",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        query.seen = True
        query.save()
        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#---------Tickets Screen API --------------------
class DoctorTicketsScreen(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

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


    def get(self , request , format=None):
        json_data = {
            "isempty" : True,
            "tickets" : [],
        }

        user = request.user

        tickets = DoctorTickets.objects.filter(doctor_id=user).order_by("-created_at")
        serializer = DoctorTicketsSerializer(tickets,many=True,context={"request":request}).data
        for i in serializer:
            created_at = self.convertdateformat(i['created_at'])
            data = {
                "id": i['id'],
                "closed" : i['closed'],
                "issues" : i['issues'],
                "timestamp" : created_at
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
            "totalappointment" : 0,
            "totalconsulted" : 0,
            "totalcancelled" : 0,
            "totalpending" : 0,
            "appointments" : [],
        }

        user = request.user
        query = Appointment.objects.filter(doctor_id=user.id).order_by("-created_at")
        appointments = query.filter(closed=True) 
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

        json_data['totalappointment'] = query.count()
        json_data['totalconsulted'] = query.filter(consulted=True,closed=True).count()
        json_data['totalcancelled'] = query.filter(cancelled=True,closed=True).count()
        json_data['totalpending'] = query.filter(closed=False).count()

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#-------Add medical records API --------------------
#---#PR1-----
class ProcedureMedicalRecords(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Getting a list of procedures that are available.
            Medical Records must be uploaded into this instance.
            Displaying only the medical records related to the doctor specialisation.
            --------------------------
            Used in patients medical records screen.
        """
        patientid = request.query_params.get("patientid",None)
        json_data = {
            "isempty" : True,
            "records" : [],
            "patient" : {},
        }

        user = request.user
        
        if patientid is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        records = MedicalRecords.objects.filter(patientid=patientid).order_by("-created_at")
        serializer = MedicalRecordsSerializer(records,many=True,context={"request":request}).data
        for i in serializer:
            if len(i['records']) > 0:
                for j in i['records']:
                    if j['deptid'] == user.department_id.id:
                        doctor = Doctor.objects.filter(id=i['created_by']).first()
                        data = {
                            "id": i['id'],
                            "title" : i['title'],
                            "created_at" : dtt.strptime(i['created_at'], YmdTHMSfz).strftime(mdY),
                            "created_by" : doctor.name
                        }
                        json_data['records'].append(data)
            else:
                doctor = Doctor.objects.filter(id=i['created_by']).first()
                data = {
                    "id": i['id'],
                    "title" : i['title'],
                    "created_at" : dtt.strptime(i['created_at'], YmdTHMSfz).strftime(mdY),
                    "created_by" : doctor.name
                }
                json_data['records'].append(data)
        
        if len(json_data['records']) > 0:
            json_data['isempty'] = False
                
        getpatient = Patient.objects.filter(id=patientid).first()

        pat_data = {
            "id" : f"{getpatient.id}",
            "name" : f"{getpatient.name}",
            "img" : f"{getpatient.img}",
            "defaultimg" : f"{getpatient.name[0:1]}",
            "gender" : f"{getpatient.gender}",
            "blood" : f"{getpatient.blood}",
        }
        json_data['patient'] = pat_data

        return display_response(
            msg = "SUCCESS",
            err= None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

    def post(self, request , format=None):
        """
            Procedure Medical Records is the main title of the records.
            Inside this multiple specialization and their records are associated 
            POST methods:
                title : [String,required] title of the procedure records
        """
        data = request.data
        user = request.user
        title = data.get("title",None)
        patientid =data.get("patientid",None)

        if title in [None,""] or patientid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_patient = Patient.objects.filter(id=patientid).first()
        if get_patient is None:
            return display_response(
                msg="FAILED",
                err="Patient not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        try:
            MedicalRecords.objects.create(
                created_by = user.id,
                title = title,
                patientid = get_patient.id
            )
            return display_response(
                msg="SUCCESS",
                err=None,
                body=None,
                statuscode=status.HTTP_200_OK
            )    
        except Exception as e:
            return display_response(
                msg="FAILED",
                err=f"{str(e)}",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

#---#AMR1-----
class AllMedicalRecords(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []
    
    def get(self , request , format=None):
        """
            Get all medical records of a current record id.
            *Testing View
        """
        recordid = request.query_params.get("recordid",None)

        if recordid is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_record = MedicalRecords.objects.filter(id=recordid).first()
        serializer = MedicalRecordsSerializer(get_record,context={"request":request}).data 
        return display_response(
            msg="SUCCESS",
            err=None,
            body=serializer,
            statuscode=status.HTTP_200_OK
        )

    def post(self , request , format=None):
        doctor = request.user
        data = request.data
        appointmentid = data.get("appointmentid",None)
        recordid = data.get("recordid",None)
        files = data.get("files",None)
        filename =data.get("filename",None)

        if appointmentid in [None,""] or recordid in [None,""] or files in [None,""] or filename in [None , ""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        records = MedicalRecords.objects.filter(id=recordid).first()
        if records is None:
            return display_response(
                msg="FAILED",
                err="Medical Records not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        serializer = MedicalRecordsSerializer(records,context={"request":request}).data
        
        get_appointment = Appointment.objects.filter(id=appointmentid).first()
        if get_appointment is None:
            return display_response(
                msg="FAILED",
                err="Appointment not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        appointment_serializer = AppointmentSerializer(get_appointment,context={"request":request}).data
        
        is_dept_exists = False
        is_dept_index = 0
        is_appointment_exists = False
        is_appointment_index = 0
        for i in serializer['records']:
            if i['deptid'] == doctor.department_id.id:
                is_dept_exists = True
                is_dept_index = serializer['records'].index(i)
                for j in i['records']:
                    if j['appointmentid'] == appointmentid:
                        is_appointment_exists = True
                        is_appointment_index = i['records'].index(j)
                        break
                break
        
        if is_dept_exists == False:
            """
                The Specialisation department is not created and must create a new one
            """
            dept_data = {
                "deptid" : doctor.department_id.id,
                "deptname" : doctor.department_id.name,
                "created_at" :str(dtt.now(IST_TIMEZONE)),
                "records" : []
            }  
            serializer['records'].append(dept_data)
            is_dept_index = -1    
        
        
        """
            else:
                The Specialisation department is created and must append the files to records
        """
        if is_appointment_exists == False:
            """
                Create an appointment record and append it to the specialisation index
            """
            appointment_data = {
                "appointmentid" : appointment_serializer['id'],
                "doctorname" : appointment_serializer['doctor']['name'],
                "date" : appointment_serializer['date'],
                "created_at" :str(dtt.now(IST_TIMEZONE)),
                "files" : []
            }
            serializer['records'][is_dept_index]['records'].append(appointment_data)
            is_appointment_index = -1

        """
            Else:
                Append the files to the appointment record files.
            Now we have the dept_index and appointment_index,so that files can be added easily
        """
        
        file_ext = files.content_type.split('/')[1]
        custom_filename = f"{files.name.split('.')[0]}_{str(uuid.uuid4())[:7]}.{file_ext}"
        final_path = f"{records.id}/{doctor.department_id.id}/{appointmentid}/{custom_filename}"
        azure_data = upload_medical_files_cloud(
            uploadfile=files,
            uploadfilename=final_path,
            uploadmime = files.content_type
        )
        if azure_data['success'] == True:
            filedata = {
                "type" :f"{file_ext}",
                "name" : f"{filename}",
                "url" : azure_data['url'],
                "username" : f"{doctor.name}",
                "userid" : f"{doctor.id}",
                "user":"doctor",
                "created_at" : str(dtt.now(IST_TIMEZONE))
            }
        else:
            return display_response(
                msg="FAILED",
                err="Failed to upload the file",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        serializer['records'][is_dept_index]['records'][is_appointment_index]['files'].append(filedata)
        records.save()

        try:
            msg = f"Your Dr. {doctor.name} has uploaded a medical records. Please find the attached file in your records section."
            create_patient_notification(
                patientid=get_appointment.patient_id,
                msg = msg
            )
        except Exception as e:
            pass

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#---#AMR2-----
class MedicalRecordsAppointments(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Getting the medical records that are available for the given specialisation.
            Get methods:
                recordid = [String,required] id of the medical records
                appointmentid = [String,optional] id of the appointment.Required necessry when displaying the records from medical appointments page
            ---------------------
            Cases:
                1)Record-ID -> Then display the records and their appointment ids with presentbookings['available'] = False and no 
                    checking required
                2)AppointmentId -> Then display the records and their appointment ids with presentbookings['available'] = True/False
                    based on checking which makes the add-new-record for current appointment available

        """
        
        json_data = {
            "isempty" : True,
            "appointments" : [],
            "presentbooking" : {
                "title" : "Add medical record for the current appointment",
                "available" : False,
                "currentappointmentid" : None,
            },
            "params" : 1,
            "recordid" : None,
        }
        doctor = request.user
        data = request.query_params
        recordid = data.get("recordid",None)
        appointmentid = data.get("appointmentid",None)
        
        if recordid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        if appointmentid not in [None,""]:
            get_appointment = Appointment.objects.filter(id=appointmentid).first()
            if get_appointment is None:
                return display_response(
                    msg="FAILED",
                    err="Appointment not found",
                    body=None,
                    statuscode=status.HTTP_400_BAD_REQUEST
                )

        get_record = MedicalRecords.objects.filter(id=recordid).first()
        serializer = MedicalRecordsSerializer(get_record,context={"request":request}).data 
        json_data['recordid'] = recordid
        for i in serializer['records']:
            if i['deptid'] == doctor.department_id.id:
                for j in i['records']: 
                    print(j['created_at'])   
                    data = {
                            "appointmentid" : j['appointmentid'],
                            "doctorname"  : j['doctorname'],
                            "date" : dtt.strptime(j['created_at'], YmdHMSfz).strftime(dBY),
                        }
                    json_data['appointments'].append(data)

        """
            Check the availability of medical records for the current appointment if
            the appointment is available
        """
        if appointmentid not in [None,""]:
            for x in json_data['appointments']:
                if x['appointmentid'] == str(appointmentid):
                    json_data['presentbooking']['available'] = True
                    json_data['presentbooking']['currentappointmentid'] = appointmentid
                    json_data['params'] = 2
                    break
        else:
            json_data['presentbooking']['available'] = True

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#---#AR1-----
class AppointmentReport(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            This views displays all the medical records files that are available in a current appointment id
            GET method:
                recordid : [String,required] medical record id
                appointmentid : [String,required] appointment id
        """
        json_data = {
            "isempty": False,
            "appointmentid": None,
            "recordid": None,
            "files": [],
        }
        user = request.user
        data = request.query_params
        recordid = data.get("recordid",None)
        appointmentid = data.get("appointmentid",None)

        if recordid in [None,""] or appointmentid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        get_record = MedicalRecords.objects.filter(id=recordid).first()
        serializer = MedicalRecordsSerializer(get_record,context={"request":request}).data
        temp = []
        for i in serializer['records']:
            if i['deptid'] == user.department_id.id:
                for j in i['records']:
                    if j['appointmentid'] == appointmentid:
                        temp = j['files']
                        break
                break   

        for x in temp:
            data = {
                "type" : x['type'],
                "name" : x['name'],
                "url" : x['url'],
                "username" : f"{x['username']}",
                "userid" : f"{x['userid']}",
                "user" : f"{x['user']}",
                "created_at" : dtt.strptime(x['created_at'], YmdHMSfz).strftime(dBY),
            }
            json_data['files'].append(data)

        json_data['appointmentid'] = appointmentid
        json_data['recordid'] = recordid

        if len(json_data['files']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg="SUCCESS",
            err=None,
            body= json_data,
            statuscode=status.HTTP_200_OK
        )

#-------Get all Patients------------
class AllPatients(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get all the patients related to this particular doctor.
            This is the search view too
            Get methods:
                search : [String,optional] search the patient by name
        """
        json_data = {
            "isempty" : True,
            "patients" : [],
        }
        user = request.user
        search = request.query_params.get('search', None)
        query = Appointment.objects.filter(doctor_id=user.id).order_by('-created_at').all()

        query_serializer = AppointmentSerializer(query,many=True,context={"request":request}).data
        temp = []
        for i in query_serializer:
            temp.append(i['patient_id'])
    
        patientids = list(set(temp))

        if search not in [None,""]:
            get_patients = Patient.objects.filter(id__in=patientids,name__icontains = search).all()
        else:
            get_patients = Patient.objects.filter(id__in=patientids).all()
        
        serializer = PatientSerializer(get_patients,many=True,context={"request":request}).data

        for x in serializer:
            data = {
                "id" : x['id'],
                "name" : x['name'],
                "img" : x['img'],
                "gender" : x['gender'],
                "defaultimg" : f"{x['name'][0:1]}",
            }
            json_data['patients'].append(data)

        if len(json_data['patients']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#------electronic Prescription----------
class ElectronicPrescription(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get the details of the electronic record id
        """
        data = request.query_params
        prescriptionid = data.get('prescriptionid',None)

        if prescriptionid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        get_prescription = MedicalPrescriptions.objects.filter(id=prescriptionid).first()
        if get_prescription is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        serializer = MedicalPrescriptionsSerializer(get_prescription,context={"request":request}).data
        return display_response(
            msg="SUCCESS",
            err=None,
            body=serializer,
            statuscode=status.HTTP_200_OK
        )

    def post(self, request):
        """
            This the method for creating for the medical prescription instance
            POST Method:
                appointmentid : [String,required] id of the appointment 
                recordid : [String,required] id of the medical record
                available : [bool,required] if the appointment is available or not  
        """
        doctor = request.user
        data = request.data
        appointmentid = data.get('appointmentid',None)
        recordid = data.get("recordid",None)
        available = data.get("available",True)

        if appointmentid in [None,""] or recordid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        """
            Check if the appointment is already added to the medical records files.
            If not then add it to the medical records files.
        """
        records = MedicalRecords.objects.filter(id=recordid).first()
        if records is None:
            return display_response(
                msg="FAILED",
                err="Medical Records not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        serializer = MedicalRecordsSerializer(records,context={"request":request}).data
        
        get_appointment = Appointment.objects.filter(id=appointmentid).first()
        if get_appointment is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        appointment_serializer = AppointmentSerializer(get_appointment,context={"request":request}).data
  
        if available == False or available == "False":
            is_dept_exists = False
            is_dept_index = 0
            is_appointment_exists = False
            is_appointment_index = 0
            for i in serializer['records']:
                if i['deptid'] == doctor.department_id.id:
                    is_dept_exists = True
                    is_dept_index = serializer['records'].index(i)
                    for j in i['records']:
                        if j['appointmentid'] == appointmentid:
                            is_appointment_exists = True
                            is_appointment_index = i['records'].index(j)
                            break
                    break
            
            if is_dept_exists == False:
                """
                    The Specialisation department is not created and must create a new one
                """
                dept_data = {
                    "deptid" : doctor.department_id.id,
                    "deptname" : doctor.department_id.name,
                    "created_at" :str(dtt.now(IST_TIMEZONE)),
                    "records" : []
                }  
                serializer['records'].append(dept_data)
                is_dept_index = -1    
            
            
            """
                else:
                    The Specialisation department is created and must append the files to records
            """
            if is_appointment_exists == False:
                """
                    Create an appointment record and append it to the specialisation index
                """
                appointment_data = {
                    "appointmentid" : appointment_serializer['id'],
                    "doctorname" : appointment_serializer['doctor']['name'],
                    "date" : appointment_serializer['date'],
                    "created_at" :str(dtt.now(IST_TIMEZONE)),
                    "files" : []
                }
                serializer['records'][is_dept_index]['records'].append(appointment_data)
                is_appointment_index = -1

                get_appointment.save()
                records.save()
                
            """
                Else:
                    Appointment id in the list already exists.
                    Create Medical Prescription instance        
            """
            

        MedicalPrescriptions.objects.create(
            patientid = get_appointment.patient_id,
            appointmentid = get_appointment.id,
            doctorid = doctor.id,
            records = {
                "title": "",
                "medicines": [],
                "created_at": dtt.now(IST_TIMEZONE).strftime(YmdTHMSfz),
            }
        )
        return display_response(
                msg="SUCCESS",
                err=None,
                body=None,
                statuscode=status.HTTP_200_OK
            )
        

    def delete(self , request , format=None):
        """
            To remove a particular data from the medicines list before generating
        """
        user = request.user
        data = request.data
        prescriptionid = data.get("prescriptionid",None)
        medicineid = data.get("medicineid",None)

        if prescriptionid in [None,""] or medicineid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        get_prescription = MedicalPrescriptions.objects.filter(id=prescriptionid).first()
        if get_prescription is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        """
            Remove the medicine which matches that medicineid
        """
        for i in get_prescription.records['medicines']:
            if str(i['medicineid']) == str(medicineid):
                get_prescription.records['medicines'].remove(i)
                get_prescription.save()
                break

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

    def put(self, request):
        """
            This view is used to update the electronic prescription of a patient
            PUT method:
                prescription : [String,required] prescription
            ------------
            Format to be sent:
                {
                    "prescriptionid" : "string-id",
                    "name": "tablet name",
                    "dosage": [0,0,0,0], #only 4 values indication mn,af,ev,nt
                    "beforefood" : bool,
                    "afterfood" : bool,
                    "qty" : int,
                    "days" : int,
                }
        """
        user = request.user
        data = request.data
        prescriptionid = data.get("prescriptionid",None)
        medname = data.get("name",None)
        dosage = data.get("dosage",None)
        beforefood = data.get("beforefood",False)
        afterfood = data.get("afterfood",False)
        qty = data.get("qty",None)
        days = data.get("days",None)


        if prescriptionid in [None,""] or medname in [None,""] or dosage in [None,""] or qty in [None,""] or days in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )      

        get_prescrip = MedicalPrescriptions.objects.filter(id=prescriptionid).first()
        if get_prescrip is None:
            return display_response(
                msg="FAILED",
                err="Medical E-Presciption Instance not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )  

        medicineid = len(get_prescrip.records['medicines'])+1

        medicinedata = {
            "medicineid" : medicineid,
            "name": medname,
            "mrng": dosage[0],
            "noon": dosage[1],
            "evening": dosage[2],
            "night": dosage[3],
            "beforefood" : beforefood,
            "afterfood" : afterfood,
            "quantity": str(qty),
            "duration": str(days),
        }

        get_prescrip.records['medicines'].append(medicinedata) 
        get_prescrip.save()

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#----Generate E-Prescription------------
def generate_pdf(json_data):
    template_path = 'index.html'
    context = json_data
    print(context)
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #if for display in browser add this line
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return {
            "res": False,
            "err": "Error in generating PDF",
        }

    final_path = context['path']

    azure_data = upload_medical_files_cloud(
        uploadfile=response,
        uploadfilename=final_path,
        uploadmime = "application/pdf"
    )
    if azure_data['success'] == True:
       return {
            "res": True,
            "err": None,
            "data" : azure_data 
        }

    return {
            "res": False,
            "err": "Error in uploading to cloud PDF",
        }
    
class GenerateEPrescription(APIView):
    
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        json_data = {
            "doctor" : {},
            "patient" : {},
            "hospital" : {
                "name" : "Sri Ramachandra Medical Hospital",
                "loc" : "Porur, Chennai",
                "phone" : "044-24242424",
            },
            "recordid" : "",
            "appointmentid" : "",
            "medicines" : [],
        }
        doctor = request.user
        data = request.query_params
        medicalid = data.get('medicalid',None)
        recordid = data.get("recordid",None)
        appointmentid = data.get("appointmentid",None)

        if medicalid is None or recordid is None or appointmentid is None:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        get_medical = MedicalPrescriptions.objects.filter(id=medicalid).first()
        if get_medical is None:
            return display_response(
                msg="FAILED",
                err="Medical E-Presciption Instance not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_record = MedicalRecords.objects.filter(id=recordid).first()
        serializer = MedicalRecordsSerializer(get_record,context={"request":request}).data
        
        get_appointment = Appointment.objects.filter(id=appointmentid).first()
        appointment_serializer = AppointmentSerializer(get_appointment,context={"request":request}).data
        if get_record is None or get_appointment is None:
            return display_response(
                msg="FAILED",
                err="Medical Record Instance not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        json_data['doctor'] = {
            "name" : f"{get_appointment.doctor['name']}",
            "department" : f"{get_appointment.doctor['specialisation']}",
            "qualification" : f"{get_appointment.doctor['qualification']}",
        }
        json_data['recordid'] = f"{recordid}"
        json_data['appointmentid'] = f"{appointmentid}"
        json_data['patient'] = {
            "name" : f"{get_appointment.patient['name']}",
            "contact" : f"{get_appointment.patient['contact']}",
            "date" : dtt.now(IST_TIMEZONE).strftime(dBYIMp),
        }

        for i in get_medical.records['medicines']:
            dosage = f"{i['mrng']}-{i['noon']}-{i['evening']}-{i['night']}".replace("True","1")
            dosage.replace("False","0")
            intake = "NS"
            if i['beforefood'] == True:
                intake = "BF"
            elif i['afterfood'] == True:
                intake = "AF"
            data = {
                "medicineid" : f"{i['medicineid']}",
                "name" : f"{i['name']}",
                "dosage" : dosage,
                "intake" :intake,
                "quantity" : f"{i['quantity']}",
                "duration" : f"{i['duration']}",
            }
            json_data['medicines'].append(data)

        custom_filename = f"{str(uuid.uuid4())[:4]}{get_medical.records['title']}-{str(uuid.uuid4())[:7]}.pdf"
        final_path = f"{get_record.id}/{request.user.department_id.id}/{appointmentid}/{custom_filename}"
        json_data['filename'] = custom_filename
        json_data['path'] = final_path

        res = generate_pdf(json_data)

        if res['res'] == True:
            """
                Add the data url to the database and in medical records
            """
            is_dept_exists = False
            is_dept_index = 0
            is_appointment_exists = False
            is_appointment_index = 0
            for i in serializer['records']:
                if i['deptid'] == doctor.department_id.id:
                    is_dept_exists = True
                    is_dept_index = serializer['records'].index(i)
                    for j in i['records']:
                        if j['appointmentid'] == appointmentid:
                            is_appointment_exists = True
                            is_appointment_index = i['records'].index(j)
                            break
                    break
        
            if is_dept_exists == False:
                """
                    The Specialisation department is not created and must create a new one
                """
                dept_data = {
                    "deptid" : doctor.department_id.id,
                    "deptname" : doctor.department_id.name,
                    "created_at" :str(dtt.now(IST_TIMEZONE)),
                    "records" : []
                }  
                serializer['records'].append(dept_data)
                is_dept_index = -1    
            
        
            """
                else:
                    The Specialisation department is created and must append the files to records
            """
            if is_appointment_exists == False:
                """
                    Create an appointment record and append it to the specialisation index
                """
                appointment_data = {
                    "appointmentid" : appointment_serializer['id'],
                    "doctorname" : appointment_serializer['doctor']['name'],
                    "date" : appointment_serializer['date'],
                    "created_at" :str(dtt.now(IST_TIMEZONE)),
                    "files" : []
                }
                serializer['records'][is_dept_index]['records'].append(appointment_data)
                is_appointment_index = -1

            """
                Else:
                    Append the files to the appointment record files.
                Now we have the dept_index and appointment_index,so that files can be added easily
            """
            filedata = {
                "type" :"pdf",
                "name" : f"{get_medical.records['title']}",
                "url" : res['data']['url'],
                "username" : f"{doctor.name}",
                "userid" : f"{doctor.id}",
                "user":"doctor",
                "created_at" : str(dtt.now(IST_TIMEZONE))
            }
            serializer['records'][is_dept_index]['records'][is_appointment_index]['files'].append(filedata)
            get_record.save()

            try:
                msg = f"Your Dr. {doctor.name} has created a medical e-prescription. Please find the attached PDF file in your records section."
                create_patient_notification(
                    patientid=get_medical.patientid,
                    msg = msg
                )
            except Exception as e:
                pass

            return display_response(
                msg="SUCCESS",
                err=None,
                body=None,
                statuscode=status.HTTP_200_OK
            )

        else:
            return display_response(
                msg="FAILED",
                err=res['err'],
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

#---Marking as Consulted/Visited View------
class AppointmentConsulted(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def put(self , request , format=None):
        """
            Marking the appointment as visited.Firstly check if the step - 2 is marked as True or not, if not true then check if the appointment
            is marked as cancelled.If the appointment is not cancelled and step-2 is True then mark the appointment as visited.
        """
        doctor = request.user
        data = request.data
        appointmentid = data.get('appointmentid',None)

        if appointmentid is None:
            return display_response(
                msg="FAILED",
                err="Appointment ID is required",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_appointment = Appointment.objects.filter(id=appointmentid).first()
        if get_appointment is None:
            return display_response(
                msg="FAILED",
                err="Appointment not found",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        serializer = AppointmentSerializer(get_appointment,context={"request":request}).data

        if serializer['closed'] == True:
            return display_response(
                msg="FAILED",
                err="Appointment is closed already",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        if serializer['cancelled'] == True:
            return display_response(
                msg="FAILED",
                err="Appointment is cancelled",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        if serializer['consulted'] == True:
            return display_response(
                msg="FAILED",
                err="Appointment is already marked as visited",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        if serializer['timeline']['step2']['completed'] == False:
            return display_response(
                msg="FAILED",
                err="Patient didn't visit the counter.Please visit the counter and then close the appointment",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        """
            Validated all steps.Now mark the appointment as visited.
            Make the activity log.
        """
        get_appointment.consulted = True
        get_appointment.closed = True
        get_appointment.timeline['step3']['completed'] = True

        activitydata = {
            "activity" : "Appointment marked as visited by doctor",
            "log" : f'''The appointment {serializer['id']} is marked as visited by doctor {doctor.name}.The ID of the doctor is {doctor.id}''',
            "created_at" : str(dtt.now(IST_TIMEZONE))
        }
        if get_appointment.activity == {}:
            get_appointment.activity = []
        
        get_appointment.activity.append(activitydata)
        get_appointment.save()

        try:
            msg = f"Your appointment #{serializer['id']} has been completed successfully.Please check medical records section for futher records"
            create_patient_notification(
                patientid=serializer['patient']['id'],
                msg = msg
            )
        except Exception as e:
            pass

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#----Analytics Screen API -----
class AppointmentAnalytics(APIView):
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
            "totalappointment" : 0,
            "totalconsulted" : 0,
            "totalcancelled" : 0,
            "totalpending" : 0,
            "appointments" : [],
        }

        doctor = request.user
        get_appointments = Appointment.objects.filter(doctor_id=doctor.id)
        serializer  = AppointmentSerializer(get_appointments,many=True,context={"request":request}).data
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
        json_data['totalappointment'] = get_appointments.count()
        json_data['totalconsulted'] = get_appointments.filter(consulted=True,closed=True).count()
        json_data['totalcancelled'] = get_appointments.filter(cancelled=True,closed=True).count()
        json_data['totalpending'] = get_appointments.filter(closed=False).count()

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#=---Time Summary Analytics API -----
class WeeklyAppointmentAnalytics(APIView):
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
            "totalappointment" : 0,
            "totalconsulted" : 0,
            "totalcancelled" : 0,
            "totalpending" : 0,
            "appointments" : [],
        }

        user = request.user

        previous_date = dtt.now() - timedelta(days=7)

        query = Appointment.objects.filter(doctor_id=user.id,created_at__gte = previous_date).order_by("-created_at")       
        appointments = query.filter(closed=True)
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

        json_data['totalappointment'] = query.count()
        json_data['totalconsulted'] = query.filter(consulted=True,closed=True).count()
        json_data['totalcancelled'] = query.filter(cancelled=True,closed=True).count()
        json_data['totalpending'] = query.filter(closed=False).count()

        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#--------Home Screen API --------------------
class HomeScreen(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        json_data = {
            "doctor" : {},
            "todaytrack" : {
                "totalappointment" : 0,
                "totalpending" : 0,
                "totalpatients" : 0,
            },
            "upcomingappointments" : {
                "totalappointment" : 0,
                "appointments" : []
            },
            "latestpatients" : {
                "isempty" : True, 
                "patients" : []
            },
            "lastappointments" : {
                "isempty" : True,
                "appointments" : []
            },
            "pendingappointments" : {
                "totalappointment" : 0,
                "appointments" : []
            },  
        }

        doctor = request.user

        """
            Get the doctor details
        """
        json_data['doctor'] = {
            "name" : f"{doctor.name}",
            "img" : f"{doctor.profile_img}",
            "id" : f"{doctor.id}",
        }

        today = dtt.now(IST_TIMEZONE).strftime(Ymd)
        query = Appointment.objects.filter(doctor_id=doctor.id)
        today_appointments = query.filter(date=today) 
        serializer = AppointmentSerializer(today_appointments,many=True,context={"request":request}).data
        
        """
            Get the today's track details
        """
        todays_patients = []
        for i in serializer:
            todays_patients.append(i['patient_id'])

        json_data['todaytrack']['totalpending'] = today_appointments.filter(closed=False).count()
        json_data['todaytrack']['totalappointment'] = today_appointments.count()
        json_data['todaytrack']['totalpatients'] = len(set(todays_patients))

        """
            Upcoming Appointments
        """
        upcoming_appointments = query.filter(closed=False,date__gte=today).order_by("-created_at")
        upcoming_serializer = AppointmentSerializer(upcoming_appointments,many=True,context={"request":request}).data
        for j in upcoming_serializer:
            data = {
                "id": j['id'],  
                "patientid": j['patient_id'],
                "patientname" : j['patient']['name'],
                "date" : dtt.strptime(j['date'],Ymd).strftime(dBY),
                "time" : dtt.strptime(j['time'],HMS).strftime(IMp),
            }   
            json_data['upcomingappointments']['appointments'].append(data)
        json_data['upcomingappointments']['totalappointment'] = upcoming_appointments.count()     

        """
            Last 7 Patients List
        """
        related_patients = query.filter(closed=True).order_by("-created_at")[:7]
        patient_serializer = AppointmentSerializer(related_patients,many=True,context={"request":request}).data
        
        all_patients = list(set([x['patient_id'] for x in patient_serializer]))
        get_patients = Patient.objects.filter(id__in=all_patients)
        patient_serializer = PatientSerializer(get_patients,many=True,context={"request":request}).data
        for k in patient_serializer:
            data = {
                "id": k['id'],
                "name" : k['name'],
                "img" : k['img'],
                "appuser" : k['appuser'],
            }
            json_data['latestpatients']['patients'].append(data)
        if len(json_data['latestpatients']['patients']) > 0: 
            json_data['latestpatients']['isempty'] = False
        
        """
            Last 7 Appointments
        """
        last_appointments = query.filter(closed=True).order_by("-created_at")[:7]
        last_serializer = AppointmentSerializer(last_appointments,many=True,context={"request":request}).data
        for l in last_serializer:
            data = {
                "id": l['id'],
                "patientid": l['patient_id'],
                "img" : l['patient']['img'],
                "patientname" : l['patient']['name'],
                "date" : dtt.strptime(l['date'],Ymd).strftime(dBY),
                "time" : dtt.strptime(l['time'],HMS).strftime(IMp),
            }
            json_data['lastappointments']['appointments'].append(data)
        
        if len(json_data['lastappointments']['appointments']) > 0:
            json_data['lastappointments']['isempty'] = False


        """
            Pending Appointments
        """
        pending_appointments = query.filter(closed=False,date__lt = today).order_by("-created_at")
        pending_serializer = AppointmentSerializer(pending_appointments,many=True,context={"request":request}).data
        for m in pending_serializer:
            data = {
                "id": m['id'],  
                "patientid": m['patient_id'],
                "patientname" : m['patient']['name'],
                "img" : m['patient']['img'],
                "date" : dtt.strptime(m['date'],Ymd).strftime(dBY),
                "time" : dtt.strptime(m['time'],HMS).strftime(IMp),
            }   
            json_data['pendingappointments']['appointments'].append(data)
        json_data['pendingappointments']['totalappointment'] = pending_appointments.count()  

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#------Drugs Search  API -----
class SearchDrugs(APIView):
    authentication_classes = [DoctorAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Search the tablets already available here
            --------------------------------
            GET method:
                search : [String,required] search query
        """
        json_data = {
            "isempty" : True,
            "search" : [],
        }

        search = request.query_params.get("search",None)
        if search is not None:
            query = Medicines.objects.filter(name__icontains=search)
            serializer = MedicinesSerializer(query,many=True,context={"request":request}).data
            for i in serializer:
                data = {
                    "id": i['id'],
                    "name" : i['name'],
                }
                json_data['search'].append(data)
            
            if len(json_data['search']) > 0:
                json_data['isempty'] = False

        return display_response(
            msg="SUCCESS",
            err=None,
            body=serializer,
            statuscode=status.HTTP_200_OK
        )



