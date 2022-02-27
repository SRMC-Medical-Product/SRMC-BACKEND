"""
    File with all the API's relating to the help desk user web
"""
from datetime import datetime as dtt,time,date,timedelta
import json
import re
from tkinter.tix import Tree
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework import status
# Create your views here.

from .models import *
from .auth import *
from .utils import *

'''Response Import'''
from myproject.responsecode import display_response,exceptiontype,exceptionmsg

'''Serializer Import'''
from .support_serializers import *
from mainapp.serializers import *
from mainapp.doctor_serializers import *

from myproject.notifications import *


#-------Login User-------
class LoginUser(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self,request,format=None):
        data = request.data
        userid = data.get("userid", None)  # Both USERID and EMail are accepted
        pin = data.get("pin", None)

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
        encrptedpin = encrypt_helpdesk_pin(pin)
        user=HelpDeskUser.objects.filter(id=userid,pin=encrptedpin)
        if user is None:
            user=HelpDeskUser.objects.filter(email=userid,pin=encrptedpin)
            if user is None:
                user=HelpDeskUser.objects.filter(mobile=userid,pin=pin)

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
            if user.activity == {}:
                formatdata = {
                    "login" :[],
                    "logout":[],
                    "log":[],
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

#---- LogOut User ----
class LogoutUser(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def post(self , request , format=None):
        user = request.user

        """
            Save Logout information on activity log
        """
        now = dtt.now(IST_TIMEZONE)
        logoutdata = {
            "date":now.strftime(dmY),
            "time":now.strftime(HMS),
        }
        user.activity['logout'].append(logoutdata)
        user.save()

        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#-----Profile Info-----
class UserProfile(APIView):  
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        ACTION = "UserData GET" 
        user = request.user

        if user in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Support User was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = HelpDeskUserSerializer(user,context={'request' :request}).data

        return display_response(
            msg = ACTION,
            err= None,
            body = serializer,
            statuscode = status.HTTP_200_OK
        )

class UserPinModify(APIView): 
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = [] 

    def put(self , request, format= None): 
        """
            Modify or Changing the Pin of the help desk user.
            First we need both oldpin and new pin, if old pin matches the user then change new pin or 
            else return not valid.
            PUT method:
                oldpin : [String,required] oldpin of the user
                newpin : [String,required] new pin of the user 
        """
        data = request.data
        user = request.user
        oldpin = data.get('oldpin') 
        newpin = data.get('newpin')
        
        if oldpin in [None , ""] or newpin in [None , ""]:
            return display_response(
                msg = "ERROR",
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        """
            Check if old pin is correct or not
        """
        encrypted_old_pin = encrypt_helpdesk_pin(oldpin)

        if user.pin != encrypted_old_pin:
            return display_response(
                msg = "ERROR",
                err= "Old Pin is not correct",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        """
            Save the new pin to the database
        """
        encrypted_new_pin = encrypt_helpdesk_pin(newpin)

        if encrypted_new_pin == encrypted_old_pin:
            return display_response(
                msg = "ERROR",
                err= "New Pin is same as old pin",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        user.pin = encrypted_new_pin
        user.save()
        
        try:
            activity = {
                "msg" : "Your login pin has been changed by you",
                "time" : dtt.now(IST_TIMEZONE).strftime(IMp),
                "date" : dtt.now(IST_TIMEZONE).strftime(dmY),
                "datetime" :str(dtt.now(IST_TIMEZONE))
            }
            user.activity['log'].append(activity)
            user.save()
        except Exception as e:
            pass

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = "Pin Changed Successfully",
            statuscode = status.HTTP_200_OK
        )

#-----Activity Log-----
class ActivityLog(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self, request , format=None):
        json_data = {
            "isempty" : True,
            "log" : []
        }
        user = request.user

        if len(user.activity['log']) > 0:
            json_data["log"] = user.activity['log']
            json_data["isempty"] = False
        
        return display_response(
            msg = "Activity Log",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#----History Appointment----
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
        """
            This view is responsible for both displaying all and querying particular appointment
            -----------
            GET method:
                search : [String,optional] search query
                filter : [String,optional] filter query [1- consulted,2-cancelled]
                sortby : [String,optional] sortby query [1-descending date,2-ascending date]
        """
        ACTION = "AppointmentsHistory GET"
        search = request.query_params.get('search',None)
        filter = str(request.query_params.get('filter',None))
        sortby = str(request.query_params.get('sortby',None))
        json_data = {
            "isempty" : True,
            "appointments" : [],
            "consultedfilter" : False,
            "cancelledfilter" : False,
            "descendingdate" : True,
            "ascendingdate" : False,
        }

        user = request.user
        s_ = HelpDeskUserSerializer(user,context={'request' :request}).data
        dept_list = list(set([e['id'] for e in s_['specialisation']]))

        query = Appointment.objects.filter(dept_id__in=dept_list,closed=True)

        if sortby == '2':
            json_data["ascendingdate"] = True
            json_data["descendingdate"] = False
            query = query.order_by('date')
        else:
            json_data["ascendingdate"] = False
            json_data["descendingdate"] = True
            query = query.order_by('-date')

        if search not in [None , ""]:
            snippet = query.filter(Q(id__icontains=search) | Q(date__icontains=search) | Q(time__icontains=search) | Q(patient__name__icontains=search) | Q(doctor__name__icontains=search))
        else:
            snippet = query

        if filter not in [None , ""]:
            if filter == "1":
                snippet = snippet.filter(consulted=True)
                json_data["consultedfilter"] = True
                json_data["cancelledfilter"] = False
            elif filter == "2":
                snippet = snippet.filter(consulted=False)
                json_data["consultedfilter"] = False
                json_data["cancelledfilter"] = True
            else:
                snippet = snippet
                json_data["consultedfilter"] = False
                json_data["cancelledfilter"] = False

        serializer = AppointmentSerializer(snippet,many=True,context={'request' :request})
        
        temp = []
        for i in serializer.data :
            temp.append({
                "id" : i['id'],
                "doctor_id" : i['doctor_id'],
                "patient_id" : i['patient_id'],
                "dept_id" : i['dept_id'],
                "patient" : i['patient'],
                "doctor" : i['doctor'],
                "date" : dtt.strptime(i['date'],Ymd).strftime(dBY),
                "time" :dtt.strptime(i['time'],HMS).strftime(IMp),
                "timeline" : i['timeline'],
                "closed" : i['closed'],
                "consulted" : i['consulted'],
                "cancelled" : i['cancelled'],
                "reassigned" : i['reassigned'],
                "activity" : i['activity'],
                "status": "Conusulted" if i['consulted'] == True else "Cancelled" 
            })


        json_data['appointments'] = temp
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#----in detail Appointment----
class InDetailAppointment(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self, request , format=None):
        aid = request.query_params.get('appointmentid',None)

        if aid in [None , ""]:
            return display_response(
                msg = "ERROR",
                err="Appointment ID not provided",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        get_appointment = Appointment.objects.filter(id=aid).first()
        if get_appointment is None:
            return display_response(
                msg = "ERROR",
                err="Appointment not found",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        serializer = AppointmentSerializer(get_appointment,context={'request' :request}).data
        serializer['date'] = dtt.strptime(serializer['date'],Ymd).strftime(dBY)
        serializer['time'] = dtt.strptime(serializer['time'],HMS).strftime(IMp)
        serializer['doctor']['pin'] = "NA"
        return display_response(
            msg = "Appointment",
            err= None,
            body = serializer,
            statuscode = status.HTTP_200_OK
        )

#---Doctors Available---------                  
class DoctorGet(APIView):
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []

    def get(self , request , format=None):
        """
            This view is responsible for both displaying all and querying doctors based on their names
            ----------------------------------------------------------------
            GET method:
                search : [String,optional] search query
                isblocked : [bool,optional] filter query 

        """
        ACTION = "Doctor GET"
        json_data = {
            "isempty" : True,
            "doctors" : [],
        }
        user = request.user
        search = request.query_params.get("search",None)
        isblocked = request.query_params.get("isblocked",False)

        s_ = HelpDeskUserSerializer(user,context={'request' :request}).data
        dept_list = list(set([e['id'] for e in s_['specialisation']]))

        snippet = Doctor.objects.filter(department_id__in=dept_list) 

        if search not in [None , ""]:
            snippet = snippet.filter(Q(name__icontains=search))

        if isblocked in [True,'True']:
            snippet = snippet.filter(is_blocked=True)
        

        serializer = DoctorSerializer(snippet,many=True,context={'request' :request})
        for i in serializer.data :
            json_data['doctors'].append([{
                "id" : i['id'],
                "doctor_id" : i['doctor_id'], 
                "name" : i['name'],
                "profile_img" : i['profile_img'],
                "specialisation" : i['specialisation'],
                "is_blocked" : i['is_blocked'],
            }]) 

        if len(json_data['doctors']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#----Doctor Details Get
class DoctorDetails(APIView): 
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []

    def get(self , request , format=None):
        """
            This view displays the particular doctor details
            ----------------------------------------------------------------
            GET method:
                doctorid : [String,required] doctor id
                appointments : [String,optional] filter query
                        1 - todays appointments
                        2 - pending appointments
                        3 - all completed appointments
        """
        ACTION = "DoctorDetails GET"
        id = request.query_params.get('doctorid',None)
        appointments_format = str(request.query_params.get('appointments',1))
        json_data = {
            "appointments" : {
                "isempty" : True,
                "appointments" : [],
                "today" : True,
                "pending" : False,
                "all" : False,
            },
            "details" : {},
            "timings" : {},
            "analytics" :  {
                "total" : 0,
                "consulted" : 0,
                "cancelled" : 0,
                "patients" : 0,
                "pending" : 0,
            }
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
        
        '''Timings'''
        timings = DoctorTimings.objects.filter(doctor_id=snippet).first()
        timings_serializer = DoctorTimingsSerializer(timings,context={'request' :request})
        json_data['timings'] = timings_serializer.data 
        
        '''Analytics'''
        appointments = Appointment.objects.filter(doctor_id=snippet.id).all()
        json_data['analytics']['total'] = appointments.count()
        json_data['analytics']['pending'] = appointments.filter(closed=False).count()
        json_data['analytics']['consulted'] = appointments.filter(consulted=True).count()
        json_data['analytics']['cancelled'] = appointments.filter(cancelled=True).count() 
        json_data['analytics']['patients'] = len(list(set([e.patient_id for e in appointments])))

        '''Appointments'''
        if appointments_format == "1":
            appointments = appointments.filter(date=dtt.today().strftime(Ymd)).all()
            json_data['appointments']['today'] = True
            json_data['appointments']['pending'] = False
            json_data['appointments']['all'] = False
        elif appointments_format == "2":
            appointments = appointments.filter(closed=False).all()
            json_data['appointments']['today'] = False
            json_data['appointments']['pending'] = True
            json_data['appointments']['all'] = False
        else:
            appointments = appointments.all()
            json_data['appointments']['today'] = False
            json_data['appointments']['pending'] = False
            json_data['appointments']['all'] = True


        appointment_serializer = AppointmentSerializer(appointments,many=True,context={'request' :request})
        json_data['appointments']['appointments'] = appointment_serializer.data

        if len(json_data['appointments']['appointments']) > 0:
            json_data['appointments']['isempty'] = False

        return display_response(
            msg = ACTION,
            err= None, 
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Patients Get--------
class PatientGet(APIView):
    authentication_classes = [HelpDeskAuthentication] 
    permission_classes = []     

    def get(self , request , format=None):
        """
            This view is responsible for both displaying all and querying patient based on their names
            ----------------------------------------------------------------
            GET method:
                search : [String,optional] search query
                primary : [bool,optional] filter query 

        """
        ACTION = "Doctor GET"
        json_data = {
            "isempty" : True,
            "patients" : [],
            "primary" : False,
        }
        user = request.user
        search = request.query_params.get("search",None)
        primaryuser = request.query_params.get("primary",False)
        
        s_ = HelpDeskUserSerializer(user,context={'request' :request}).data
        dept_list = list(set([e['id'] for e in s_['specialisation']]))

        appointments = Appointment.objects.filter(dept_id__in=dept_list).all()
        all_patients = list(set([e.patient_id for e in appointments]))
        
        snippet = Patient.objects.filter(id__in=all_patients).all()
        
        if primaryuser in [True , "True"]:
            snippet = snippet.filter(primary=True)
            json_data['primary'] = True

        if search not in [None , ""]:
            snippet = snippet.filter(Q(name__icontains=search))
        
        serializer = PatientSerializer(snippet,many=True,context={'request' :request}).data

        json_data['patients'] = serializer

        if len(json_data['patients']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Patient Details Get--------
class PatientDetails(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            This view displays the particular doctor details
            ----------------------------------------------------------------
            GET method:
                patientid : [String,required] patient id
                appointments : [String,optional] filter query
                        1 - todays appointments
                        2 - pending appointments
                        3 - all completed appointments
        """
        ACTION = "Patient Details GET"
        id = request.query_params.get('patientid',None)
        appointments_format = str(request.query_params.get('appointments',1))
        json_data = {
            "appointments" : {
                "isempty" : True,
                "appointments" : [],
                "today" : True,
                "pending" : False,
                "all" : False,
            },
            "details" : {},
            "analytics" :  {
                "total" : 0,
                "consulted" : 0,
                "cancelled" : 0,
                "doctors" : 0,
                "pending" : 0,
            }
        }
        if id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        snippet = Patient.objects.filter(id=id).first()
        serializer = PatientSerializer(snippet,context={'request' :request}).data
        
        '''Details'''
        json_data['details'] = serializer

        '''Analytics'''
        appointments = Appointment.objects.filter(patient_id=snippet.id).all()
        json_data['analytics']['total'] = appointments.count()
        json_data['analytics']['pending'] = appointments.filter(closed=False).count()
        json_data['analytics']['consulted'] = appointments.filter(consulted=True).count()
        json_data['analytics']['cancelled'] = appointments.filter(cancelled=True).count() 
        json_data['analytics']['doctors'] = len(list(set([e.doctor_id for e in appointments])))

        '''Appointments'''
        if appointments_format == "1":
            appointments = appointments.filter(date=dtt.today().strftime(Ymd)).all()
            json_data['appointments']['today'] = True
            json_data['appointments']['pending'] = False
            json_data['appointments']['all'] = False
        elif appointments_format == "2":
            appointments = appointments.filter(closed=False).all()
            json_data['appointments']['today'] = False
            json_data['appointments']['pending'] = True
            json_data['appointments']['all'] = False
        else:
            appointments = appointments.all()
            json_data['appointments']['today'] = False
            json_data['appointments']['pending'] = False
            json_data['appointments']['all'] = True


        appointment_serializer = AppointmentSerializer(appointments,many=True,context={'request' :request})
        json_data['appointments']['appointments'] = appointment_serializer.data

        if len(json_data['appointments']['appointments']) > 0:
            json_data['appointments']['isempty'] = False

        return display_response(
            msg = ACTION,
            err= None, 
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Appointment In Detail --------
class AppointmentUpdateArrived(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def put(self, request , format=None):
        """
            This view updates the appointments details of steps 2
            Put method:
                appointmentid : [String,required] id of the appointment
        """    
        aid = request.data.get('appointmentid',None)
        if aid in [None , ""]:
            return display_response(
                msg = "ERROR",
                err= "AID Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        query = Appointment.objects.filter(id=aid).first()
        serializer = AppointmentSerializer(query,context={'request' :request}).data
        
        """
            Update the step-2 appointment in timeline
        """
        step2 = serializer['timeline']['step2']['completed']
        if step2 is True:
            return display_response(
                msg = "ERROR",
                err= "Step 2 already completed",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        query.timeline['step2']['completed'] = True
        query.timeline['step2']['time'] = str(dtt.now(IST_TIMEZONE).strftime(HMS))
        query.save()

        try:
            pat_msg = f"Your presence in hospital is confirmed for the appointment {query.id}. Please wait for the doctor to arrive."
            create_patient_notification(
                msg=pat_msg,
                patientid=query.patient_id,
            )
        except Exception as e:
            pass

        return display_response(
            msg = "SUCCESS",
            err= None,  
            body = serializer,
            statuscode = status.HTTP_200_OK  
        )

#---Cancel Single Appointment
class AppointmentCancel(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def put(self, request , format=None):
        """
            This view cancels the appointments permanently
            PUT method:
                appointmentid : [String,required] id of the appointment
                reason : [String,required] reason for cancellation

        """    
        aid = request.data.get('appointmentid',None)
        reason = request.data.get('reason', None)
        if aid in [None , ""] or reason in [None,""]:
            return display_response(
                msg = "ERROR",
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        query = Appointment.objects.filter(id=aid).first()
        serializer = AppointmentSerializer(query,context={'request' :request}).data
        
        """
            Update the appointment as cancelled and closed == True and update the timeline
        """
        if query.closed == True:
            return display_response(
                msg = "ERROR",
                err= "Appointment already closed",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        if query.cancelled == True:
            return display_response(
                msg = "ERROR",
                err= "Appointment already cancelled",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        query.timeline['cancel']['completed'] = True
        query.timeline['cancel']['time'] = str(dtt.now(IST_TIMEZONE).strftime(HMS))
        query.cancelled = True
        query.closed = True

        user_serializer = HelpDeskUserSerializer(request.user,context={'request' :request}).data

        activity = {
            "activity" : "Cancelled",
            "reason" : reason,
            "datetime" : str(dtt.now(IST_TIMEZONE)),
            "time" : str(dtt.now(IST_TIMEZONE).strftime(HMS)),
            "user" : user_serializer
        }

        if query.activity == {}:
            data = {
                "cancel" : activity,
            }
            query.activity = data
        else:
            query.activity['cancel'] = activity
    
        try:
            pat_msg = f"Your appointment {query.id} has been cancelled. Please contact the counter for further details."
            create_patient_notification(
                msg=pat_msg,
                patientid=query.patient_id,
            )
        except Exception as e:
            pass

        query.save()

        return display_response(
            msg = "SUCCESS",
            err= None,  
            body = serializer,
            statuscode = status.HTTP_200_OK  
        )

#---Tickets --------------------------------
class AllPatientTickets(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get all the tickets of the patients
            ---------------------
            GET method:
                closed : [bool,optional] closed or open
                search : [String,optional] search the tickets by patient name
        """
        json_data = {
            "isempty" : True,
            "tickets" : [],
            "selected_closed" : False,
        }

        params = request.query_params
        search = params.get("search",None)
        closed = params.get("closed",False)
        
        user = request.user
        user_serializer = HelpDeskUserSerializer(user,context={'request' :request}).data
        depts_list = [x['id'] for x in user_serializer['specialisation']]
        
        get_depts = Department.objects.filter(id__in=depts_list)
        query = PatientTickets.objects.filter(dept__in = get_depts).order_by('-created_at')
 
        if closed in [True ,'True']:
            query = query.filter(closed=True)
            json_data['selected_closed'] = True
        else:
            query = query.filter(closed=False)
            json_data['selected_closed'] = False
        
        if search not in [None , ""]:
            query = query.filter(Q(user_id__name__icontains=search))

        serializer = PatientTicketsSerializer(query,many=True,context={'request' :request}).data
        for i in serializer:
            data = {
                "id" : i['id'],
                "closed" : i['closed'],
                "created_at" : dtt.strptime(i['created_at'],YmdTHMSfz).strftime(dBYIMp),
                "name" : i['user_id']['name'],
                "userid" : i['user_id']['id'],
                "mobile" : i['user_id']['mobile']
            }
            json_data['tickets'] = data


        if len(json_data['tickets']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

class AllDoctorTickets(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get all the tickets of the doctor
            ---------------------
            GET method:
                closed : [bool,optional] closed or open
                search : [String,optional] search the tickets by doctor name
        """
        json_data = {
            "isempty" : True,
            "tickets" : [],
            "selected_closed" : False,
        }

        params = request.query_params
        search = params.get("search",None)
        closed = params.get("closed",False)
        
        user = request.user
        user_serializer = HelpDeskUserSerializer(user,context={'request' :request}).data
        depts_list = [x['id'] for x in user_serializer['specialisation']]
        
        get_depts = Department.objects.filter(id__in=depts_list)
        query = DoctorTickets.objects.filter(dept__in = get_depts).order_by('-created_at')
 
        if closed in [True ,'True']:
            query = query.filter(closed=True)
            json_data['selected_closed'] = True
        else:
            query = query.filter(closed=False)
            json_data['selected_closed'] = False
        
        if search not in [None , ""]:
            query = query.filter(Q(user_id__name__icontains=search))

        serializer = DoctorTicketsSerializer(query,many=True,context={'request' :request}).data
        for i in serializer:
            data = {
                "id" : i['id'],
                "closed" : i['closed'],
                "created_at" : dtt.strptime(i['created_at'],YmdTHMSfz).strftime(dBYIMp),
                "name" : i['doctor_id']['name'],
                "userid" : i['doctor_id']['id'],
                "mobile" : i['doctor_id']['phone']
            }
            json_data['tickets'] = data


        if len(json_data['tickets']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )


#----Cancel All Appointments of a doctor --------------------------------
class CancelAllAppointments(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def post(self , request , format=None):
        """
            Cancel all the appointments of the doctor
            ---------------------
            POST method:
                doctor_id : [int,required] doctor id
                reason : [String,required] reason for cancelling
                date : [String,required] date of the appointment in YYYY-MM-DD format
        """

        params = request.data
        doctor_id = params.get("doctor_id",None)
        reason = params.get("reason",None)
        date = params.get("date",None)
        user = request.user

        if doctor_id in [None , ""] or date in [None,""]or reason in [None , ""]:
            return display_response(
                msg = "FAILURE",
                err= "doctor_id or reason is missing",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )


        """
            Check if the doctor exists
        """
        get_doctor = Doctor.objects.filter(id=doctor_id).first()
        if get_doctor is None:
            return display_response(
                msg = "FAILURE",
                err= "Doctor does not exist",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )
        dateformat = dtt.strptime(date,Ymd)
        query = Appointment.objects.filter(doctor_id = get_doctor.id,date=dateformat).order_by('-created_at')
        serializer = AppointmentSerializer(query,many=True,context={'request' :request}).data

        if query.count() > 0:
            for i in query:
                """
                    Check if the appointments is already closed,if closed then skip
                    or else mark it as cancelled
                """
                if i.closed == True:
                    pass
                else:
                    """
                        1.Cancel the appointment
                        2.Set Activity Log
                        3.Create Notifications
                    """
                    i.timeline['cancel']['completed'] = True
                    i.timeline['cancel']['time'] = str(dtt.now(IST_TIMEZONE).strftime(HMS))
                    i.cancelled = True
                    i.closed = True

                    user_serializer = HelpDeskUserSerializer(user,context={'request' :request}).data

                    activity = {
                        "activity" : "Cancelled",
                        "reason" : reason,
                        "datetime" : str(dtt.now(IST_TIMEZONE)),
                        "time" : str(dtt.now(IST_TIMEZONE).strftime(HMS)),
                        "user" : user_serializer
                    }

                    if i.activity == {}:
                        data = {
                            "cancel" : activity,
                        }
                        i.activity = data
                    else:
                        i.activity['cancel'] = activity
                
                    try:
                        pat_msg = f"Your appointment {i.id} has been cancelled. Please contact the counter for further details."
                        create_patient_notification(
                            msg=pat_msg,
                            patientid=i.patient_id,
                        )
                    except Exception as e:
                        pass

                    i.save()

        try:
            doc_msg = f"Your upcoming appointment for the day has been cancelled. Please contact the counter for further details."
            create_doctor_notification(
                msg=doc_msg,
                doctorid=str(get_doctor.id)
            )
        except Exception as e:
            pass
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = None,
            statuscode = status.HTTP_200_OK
        )

#---Get all Appointments --------------------------------
class GetAllAppointments(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get all the appointments here.
            ---------------------
            GET method:
                set : [String,required] set of the appointments
                    1 - Live Today 
                    2 - Previous Date pending
                    3 - Upcoming
                    4 - History (closed)
                    5 - All
                search : [String,optional] search the appointments
        """
        json_data ={
            "isempty" : True,
            "livetoday" : True,
            "pending" : False,
            "upcoming" : False,
            "history" : False,
            "all" : False,
            "count" : 0,
            "patientnames" : [],
            "appointments" : []
        }
        aset = str(request.query_params.get("set",1))
        search = request.query_params.get("search",None)

        user = request.user
        user_serializer = HelpDeskUserSerializer(user,context={'request' :request}).data
        depts_list = [x['id'] for x in user_serializer['specialisation']]

        if aset in [1,'1']:
            appointments = Appointment.objects.filter(date=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False,dept__id__in = depts_list).order_by('-time')
            json_data['livetoday'] = True
            json_data['pending'] = False
            json_data['upcoming'] = False
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [2,'2']:
            appointments = Appointment.objects.filter(date__lt=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False,dept__id__in = depts_list).order_by('-date')
            json_data['livetoday'] = False
            json_data['pending'] = True
            json_data['upcoming'] = False
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [3,'3']:
            appointments = Appointment.objects.filter(date__gt=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False,dept__id__in = depts_list).order_by('date')
            json_data['livetoday'] = False
            json_data['pending'] = False
            json_data['upcoming'] = True
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [4,'4']:
            appointments = Appointment.objects.filter(closed=True,dept__id__in = depts_list).order_by('-date')
            json_data['livetoday'] = False
            json_data['pending'] = False
            json_data['upcoming'] = False
            json_data['history'] = True
            json_data['all'] = False
        else:
            appointments = Appointment.objects.filter(dept__id__in = depts_list).order_by('-date')
            json_data['livetoday'] = False
            json_data['pending'] = False
            json_data['upcoming'] = False
            json_data['history'] = False
            json_data['all'] = True

        if search not in [None , ""]:
            query = appointments.filter(Q(patient__name__icontains=search) | Q(doctor__name__icontains=search) | Q(id__icontains=search))
            #appointments.filter(Q(id__icontains = id) | Q(patient__name__icontains = search) | Q(patient__phone__icontains = search) | Q(patient__email__icontains = search) | Q(doctor__name__icontains = search) | Q(doctor__phone__icontains = search) | Q(doctor__email__icontains = search) | Q(date__icontains = search) | Q(time__icontains = search) | Q(reason__icontains = search) | Q(status__icontains = search) | Q(closed__icontains = search) | Q(created_at__icontains = search) | Q(updated_at__icontains = search))
        else:
            query = appointments

        serializer = AppointmentSerializer(query,many=True,context={'request' :request}).data
        
        temp = []
        for i in serializer:
            data = {
                "id" : i['id'],
                "date" : dtt.strptime(i['date'] , Ymd).strftime(dBY),
                "time" :  dtt.strptime(i['time'] , HMS).strftime(IMp),
                "patient_id" : i['patient_id'],
                "patient_name" : i['patient']['name'],
                "doctor_id" : i['doctor_id'],
                "doctor_name" : i['doctor']['name'],
                "consulted" : i['consulted'],
                "cancelled" : i['cancelled'],
                "closed" : i['closed'],
                "status" : "Consulted" if i['consulted']==True else "Cancelled" if i['cancelled']== True else "Pending",
                "open" : True if i['closed'] == False else False,
            }
            json_data['patientnames'].append({
                "id" : i['id'],
                "name" : i['patient']['name'],
            })
            temp.append(data)

        json_data['appointments'] = temp

        if len(json_data['appointments']) > 0:
            json_data['count'] = len(json_data['appointments'])
            json_data['isempty'] = True
    
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Overview and Analytics --------------------
class OverviewAndAnalytics(APIView):
    authentication_classes = [HelpDeskAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        json_data ={
            "isempty" : True,
            "upcomingcount" : 0,
            "livetodaycount" : 0,
            "pendingcount" : 0,
            "historycount" : 0,
            "allcount" : 0,
            "upcomingappointments" : [],
            "liveappointments" : [],
        }

        user = request.user
        user_serializer = HelpDeskUserSerializer(user,context={'request' :request}).data
        depts_list = [x['id'] for x in user_serializer['specialisation']]

        query = Appointment.objects.filter(dept__id__in = depts_list).order_by('date')

        upcomingappointments = query.filter(date__gt=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False)
        liveappointments = query.filter(date=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False)

        json_data['upcomingcount'] = upcomingappointments.count()
        json_data['livetodaycount'] = liveappointments.count()
        json_data['pendingcount'] = query.filter(closed=False).count()
        json_data['historycount'] = query.filter(closed=True).count()
        json_data['allcount'] = query.count()

        upcoming_serializer = AppointmentSerializer(upcomingappointments,many=True,context={'request' :request}).data

        for i in upcoming_serializer:
            data = {
                "id" : i['id'],
                "date" : dtt.strptime(i['date'] , Ymd).strftime(dBY),
                "time" :  dtt.strptime(i['time'] , HMS).strftime(IMp),
                "patient_id" : i['patient_id'],
                "patient_name" : i['patient']['name'],
                "doctor_id" : i['doctor_id'],
                "doctor_name" : i['doctor']['name'],
                "consulted" : i['consulted'],
                "cancelled" : i['cancelled'],
                "closed" : i['closed'],
                "status" : "Consulted" if i['consulted']==True else "Cancelled" if i['cancelled']== True else "Pending",
                "open" : True if i['closed'] == False else False,
            }
            json_data['upcomingappointments'].append(data)

        live_serializer = AppointmentSerializer(liveappointments,many=True,context={'request' :request}).data

        for x in live_serializer:
            data = {
                "id" : x['id'],
                "date" : dtt.strptime(x['date'] , Ymd).strftime(dBY),
                "time" :  dtt.strptime(x['time'] , HMS).strftime(IMp),
                "patient_id" : x['patient_id'],
                "patient_name" : x['patient']['name'],
                "doctor_id" : x['doctor_id'],
                "doctor_name" : x['doctor']['name'],
                "consulted" : x['consulted'],
                "cancelled" : x['cancelled'],
                "closed" : x['closed'],
                "status" : "Consulted" if x['consulted']==True else "Cancelled" if x['cancelled']== True else "Pending",
                "open" : True if x['closed'] == False else False,
            }
            json_data['liveappointments'].append(data)


        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )
        








