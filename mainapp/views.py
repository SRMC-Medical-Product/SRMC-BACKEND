"""
    File with all API's relating to the patient app

"""
from logging.config import valid_ident
from pydoc import doc
from re import S
from django.utils import timezone
from django.db.models import Q
import calendar

from datetime import datetime as dtt,time,date,timedelta
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from myproject.responsecode import display_response

from .models import *
from myproject.notifications import *
from .auth import *
from .serializers import *
from mainapp.doctor_serializers import *
from .tasks import test_func
from .utils import *
from myproject.infocontent import *

#------Profile Lists
REALTION = ["Father","Mother","Brother","Sister","Husband","Wife","Son","Daughter","Grandfather","Grandmother","Grandson","Granddaughter","Friend","Other"]
GENDER = ["Male","Female","Other"]
BLOOD = ["A+","A-","B+","B-","O+","O-","AB+","AB-"]


#---------Appointment Booking Function-----
def make_appointment_booking(patient_id_,date_,time_,doctor_id_):
    #TODO: validate if the patient id given is self or family member of a user....Date:16/02/2022-Aravind-unsolved
    #TODO: validate if the time and date is present in doctor schedule......Date:16/02/2022-Aravind-unsolved 
    """
        API to book appoinment
        Allowed methods:
            -POST
        
        Authentication: Required UserAuthentication

        POST:
            data:
                patient_id: [string,required] id of the patient
                date:       [string,required,format: mm/dd/yyyy] date of appoinment
                time:       [string,required,format: hh:mm:ss] time for the appoinment
                doctor_id:  [ string,required] id of the doctor

    """
    patiend_id=patient_id_
    date=date_
    time=time_
    doctor_id=doctor_id_

    validation_arr=["",None]
        
    """validate data"""
    if patiend_id in validation_arr or date in validation_arr or time in validation_arr or doctor_id in validation_arr:

        dataout = {
            "MSG":"FAILED",
            "ERR":"Invalid data given",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
            }
        return dataout
        
    doctor_=Doctor.objects.filter(id=doctor_id) #get doctor instance

    if doctor_.exists():
        doctor_=doctor_[0]
    else:
        dataout = {
            "MSG":"FAILED",
            "ERR":"Invalid doctor id given",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout

    patient_=Patient.objects.filter(id=patiend_id)  #get patient instance

    if patient_.exists():
        patient_=patient_[0]
        
    else:
        dataout = {
            "MSG":"FAILED",
            "ERR":"Invalid patient id given",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout

    appuser = User.objects.filter(id=patient_.appuser).first() #Get the app user instance
    if appuser is None:
        dataout = {
            "MSG":"FAILED",
            "ERR":"User does not exists for the patient",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout

    doctor_timings_=DoctorTimings.objects.filter(doctor_id=doctor_)   #get doctor timings instance

    if doctor_timings_.exists():
        doctor_timings_=doctor_timings_[0]
    else:
        dataout = {
            "MSG":"FAILED",
            "ERR":"Invalid doctor id given",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout    
    timeslots_json=doctor_timings_.timeslots

    print(date)
    print(time)
    print(timeslots_json)

    #update doctor timeslot  by increasing the count
    try:
        timeslots_json=update_time_slots_json_for_appoinment(timeslots_json,date,time)
    except Exception as e:
        dataout = {
            "MSG" :"FAILED",
            "ERR" : "Date or Time slot for the particular doctor is invalid",
            "BODY" : None,
            "STATUS" : status.HTTP_400_BAD_REQUEST
        }
        return dataout

    timeline_data = {
        "step1":{
            "title" : "Booking Confirmed",
            "time" :dtt.now().time().strftime("%H:%M:%S"),
            "completed" : True
                },
        "step2":{
            "title" : "Arrived at Hospital",
            "time" : "",
            "completed" : False,
                },
        "step3":{
            "title" : "Consulted",
            "time" :"",
            "completed" : False
                },
        "cancel":{
            "title" : "Cancelled",
            "time" : "",
            "completed" : False
        }
    }
    time_line=timeline_data
        
    date_date=return_date_type(date)   #convert string date to date object
    time_time=return_time_type(time)    #convert string time to time object

    doctor_serialized_data=DoctorSerializer(doctor_,context={"request":request}).data
    patient_serialized_data=PatientSerializer(patient_,context={"request":request}).data
    patient_serialized_data['contact'] = appuser.mobile

    deptment = Department.objects.filter(id=doctor_serialized_data['department_id']['id']).first()
    if deptment is None:
        dataout = {
            "MSG" : "FAILED",
            "ERR" : "Invalid department id given",
            "BODY":None,
            "STATUS" : status.HTTP_400_BAD_REQUEST
        }
        return dataout

    """ Populate appoinment model """
    a=Appointment.objects.create(
                    date=date_date,
                    time=time_time,
                    doctor_id=doctor_id,
                    patient_id=patiend_id,
                    dept_id = deptment.id,
                    timeline=time_line,
                    counter = deptment.counter,
                    doctor=doctor_serialized_data,
                    patient=patient_serialized_data
                            )
    appoinment_serializer=AppointmentSerializer(a).data

    doctor_timings_.timeslots=timeslots_json               #update doctor timings
    doctor_timings_.save(update_fields=["timeslots"])

    """ Populate HelpDeskAppoinment model for a particular date"""
    help_desk_appoinment_instance=HelpDeskAppointment.objects.get_or_create(date=date_date,department=doctor_.department_id)[0]
        
    help_desk_appoinment_instance.count=help_desk_appoinment_instance.count+1  #increment the count of appoinment for th date
        
    arr=help_desk_appoinment_instance.bookings   #add appoinments to json
    arr.append(appoinment_serializer)
    help_desk_appoinment_instance.bookings=arr
        
    help_desk_appoinment_instance.save()     #save the helpdeskappoinment instance

    try:
        """ Add doctor notification """
        doc_msg = f"You have an appointment booked on {dtt.strptime(str(a.date),Ymd).strftime(dBY)},{dtt.strptime(str(a.time),HMS).strftime(IMp)}."
        DoctorNotification.objects.create(doctor_id=doctor_,message=doc_msg)
    except Exception as e:
        pass

    try:
        """ Add doctor notification """
        pat_msg = f"Your appointment booking on {dtt.strptime(str(a.date),Ymd).strftime(dBY)},{dtt.strptime(str(a.time),HMS).strftime(IMp)} with Dr. {a.doctor['name']} has been booked."
        PatientNotification.objects.create(patientid=appuser,message=pat_msg)
    except Exception as e:
        pass

    dataout = {
        "MSG":"SUCCESS",
        "ERR":None,
        "BODY":"Appoinment Booked successfully",
        "STATUS": status.HTTP_200_OK
    }
    return dataout

#---------Register View for Patient-----------------
def register_new_user(number_,name_):
    number=number_
    name = name_

    #validating the mobile number
    if number in ["",None] or len(number)!=10:
        dataout = {
            "MSG":"FAIL",
            "ERR":"Please provided user data(mobile number)",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout
    #validating the user name
    if name in ["",None]:
        dataout = {
            "MSG":"FAIL",
            "ERR":"Please provide user data(name)",
            "BODY":None,
            "STATUS":status.HTTP_400_BAD_REQUEST
        }
        return dataout

    #gets the userinstance in case of old user or creates a new user instance        
    user_instance=User.objects.filter(mobile=number).first()
    if user_instance is not None:
        return display_response(
            msg="FAIL",
            err="User already exist.Try signin",
            body=None,
            statuscode=status.HTTP_406_NOT_ACCEPTABLE
        )
    
    patient_instance=Patient.objects.create(
        name=name,
        primary=True,
        relation="User",
        #img: "PATIENT_TODO_IMG"
    )
    user_instance=User.objects.get_or_create(mobile=number,name=name,patientid=patient_instance.id)[0]
    patient_instance.appuser = user_instance.id
    patient_instance.save()
    user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]
        
    if user_otp_instance is not None :
        user_otp_instance.delete()

        
    user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]
    print(user_otp_instance.otp)
    print(user_otp_instance.code)
    return {
                "MSG":"SUCCESS",
                "ERR":None,
                "BODY":{
                    "otp":user_otp_instance.otp,
                    "code":user_otp_instance.code,
                    "patientid": patient_instance.id
                        },
                "STATUS":status.HTTP_200_OK
                }


#--------LoginUser API--------
class LoginUser(APIView):

    """
        This view is responsible for both login and register of the user
        If the user is new then he is registered in the database
        
        methods:
            -POST

        POST data:mobile number of the user

        return: dict of otp and secret code
    
    """

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,fromat=None):

        data=request.data
        
        number=data.get("number",None)

        #validating the mobile number
        if number in ["",None] or len(number)!=10:
            return Response({
                        "MSG":"FAIL",
                        "ERR":"Please provided user data(mobile number)",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)


        #gets the userinstance in case of old user or creates a new user instance        
        user_instance=User.objects.filter(mobile=number).first()
        if user_instance is None:
            return display_response(
                msg="FAIL",
                err="User does not exist.Try signup",
                body=None,
                statuscode=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]
        
        if user_otp_instance is not None:
            user_otp_instance.delete()
        
        user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]
        print(user_otp_instance.otp)
        print(user_otp_instance.code)
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":{
                        "otp":user_otp_instance.otp,
                        "code":user_otp_instance.code
                            }
                        },status=status.HTTP_200_OK)

#-------RegisterUser API--------
class RegisterUser(APIView):

    """
        This view is responsible for both login and register of the user
        If the user is new then he is registered in the database
        
        methods:
            -POST

        POST data:mobile number of the user

        return: dict of otp and secret code
    
    """

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,fromat=None):

        data=request.data
        
        number=data.get("number",None)
        name = data.get("name",None)

        #validating the mobile number
        if number in ["",None] or len(number)!=10:
            return display_response(
                msg="FAIL",
                err="Please provided user data(mobile number)",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        #validating the user name
        if name in ["",None]:
            return display_response(
                msg="FAIL",
                err="Please provide user data(name)",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        try:
            res = register_new_user(number,name)
            return display_response(
                msg=res["MSG"],
                err=res["ERR"],
                body=res["BODY"],
                statuscode=res["STATUS"]
            )
        except Exception as e:
            return display_response(
                msg="FAIL",
                err=str(e),
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

#-------Validate User API --------
class ValidateUser(APIView):
    
    """
        APIView to validate the user otp and generate the authentication token

        methods:
            -POST
        
        POST data: otp and code

        return:
            json web token

    """

    authentication_classes=[]
    permission_classes=[]

    def post(self,request,format=None):

        data=request.data

        otp=data.get("otp")
        code=data.get("code")

        try:
            user_otp_instance=UserOtp.objects.get(otp=otp,code=code)
        
        except:
            return Response({
                        "MSG":"Failed",
                        "ERR":"Invalid otp or code",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
        
        if user_otp_instance.expiry_time>=timezone.now():
            token=generate_token({
                        "id":user_otp_instance.user.id
                                })
            user_otp_instance.delete()
        else:
            return Response({
                        "MSG":"Failed",
                        "ERR":"Invalid otp or code time",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":{
                        "token":token
                            }
                        },status=status.HTTP_200_OK)

#------USer Profile API's-----------
class UserProfile(APIView):

    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def get(self,request,format=None):
        """
            This view is responsible for getting the user profile and other patients details too when id is passed
            GET method: 
                patientid : [String,optional] The id of the patient
        """
        json_data = {
            "profile" : {},
            "relation" : REALTION,
            "gender" : GENDER,
            "blood" : BLOOD,
            "user" : {}
        }
        patientid = request.query_params.get("patientid",None)
        
        if patientid in [None,""]:
            query = Patient.objects.filter(id=request.user.patientid).first()
        else:
            query = Patient.objects.filter(id=patientid).first()
            if query is None:
                return display_response(
                    msg="FAIL",
                    err="Patient does not exist",
                    body=None,
                    statuscode=status.HTTP_406_NOT_ACCEPTABLE
                )
            
        serializer=PatientSerializer(query,context={"request":request}).data
        print(serializer)
        json_data['profile']=serializer
        print(json_data['profile'])
        if serializer['dob'] not in [None , ""]:
          json_data['profile']['dob'] = dtt.strptime(serializer['dob'],Ymd).strftime(dmY)
        json_data['profile'].__setitem__('defaultimg' , serializer['name'][0:1])
        json_data['profile'].__setitem__('phone',request.user.mobile)
        json_data['user']=UserSerializer(request.user,context={"request":request}).data

        # test_func.delay()
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":json_data
                        },status=status.HTTP_200_OK)
    
    def put(self,request):
        """
            This view is responsible for getting the user profile and other patients details too when id is passed
            GET method: 
                patientid : [String,optional] The id of the patient. If patientid s present then it reporesent oher patient or else app user as patient
        """

        user=request.user
        data=request.data
        patientid = data.get("patientid",None)
        name=data.get("name",None)     
        relation =data.get("relation",None) 
        gender =data.get("gender",None)
        blood =data.get("blood",None)
        dob =data.get("dob",None)
        email=data.get("email",None)
        img =data.get("img",None)
        aadhar=data.get("aadhar",None) #optional              
        
        validation_arr = ["",None,"null"]
        print(request.data)
        if patientid in validation_arr:
            patient = Patient.objects.filter(id=user.patientid).first()
        else:
            patient = Patient.objects.filter(id=patientid).first()
            if patient is None:
                return display_response(
                    msg="FAIL",
                    err="Patient does not exist",
                    body=None,
                    statuscode=status.HTTP_406_NOT_ACCEPTABLE
                )
        if patient is None:
            return display_response(
                msg="FAIL",
                err="User does not exist",
                body=None,
                statuscode=status.HTTP_406_NOT_ACCEPTABLE
            )
        if name not in validation_arr:
            patient.name=name
            user.name=name
            patient.save()
            user.save()
 
        if img not in validation_arr:
            patient.img = img
            user.img = img
            patient.save()
            user.save()
 
        if email not in validation_arr:
            patient.email = email
            patient.save()
        
        if relation not in validation_arr:
            patient.relation = relation
            patient.save()

        if gender not in validation_arr:
            patient.gender = gender
            patient.save()

        if blood not in validation_arr:
            patient.blood = blood
            patient.save()

        if dob not in validation_arr:
            dob_format = dtt.strptime(dob,dmY).strftime(Ymd)
            patient.dob= dob_format
            patient.save()
        
        print(img)
        print(patient.img)
        print(type(img))
        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

#-------Family Members API's-------
class FamilyMembers(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        json_data = {
            "isempty": True,
            "user" : {}, 
        } 

        serializer=UserSerializer(request.user)
        json_data['user']=serializer.data
        
        if json_data['user']['family_members'] is not None:
            for i in json_data['user']['family_members']:
                i.__setitem__('defaultimg' , i['name'][0:1])
 
            if len(json_data['user']['family_members']) > 0:
                json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err = None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

    def post(self,request,format=None):

        """
            API View to add family member to a particular user
            With the given data a new user instance is created.

            Allowed Methods:
                -POST
            
            Request data:
                name:   [String,required] name of the patient
                relation  [String,required] relation to the patient
                email:  [String] email id of the patient
                aadhar: [String] aadhar number of the patient

            Authentication:
                -Required
                -UserAuthentication
        
        """
        user=request.user
        data=request.data

        name=data.get("name",None)     #required
        relation =data.get("relation",None) #required
        gender =data.get("gender",None)
        blood =data.get("blood",None)
        dob =data.get("dob",None)
        email=data.get("email",None)
        img =data.get("img",None)
        aadhar=data.get("aadhar",None) #optional

        #validating the user data
        if name in [None,""] or relation in [None,""]:

            return Response({
                    "MSG":"FAILED",
                    "ERR":"Please provide valid name and number",
                    "BODY":None
                         },status=status.HTTP_404_NOT_FOUND)
        
        patient_instance = Patient.objects.create(
            relation=relation,
            name=name,
            primary=False,
            appuser = user.id
        )
        if gender not in [None,""]:
            patient_instance.gender = gender
            patient_instance.save()
        if blood not in [None,""]:
            patient_instance.blood = blood
            patient_instance.save()
        if dob not in [None,""]:
            patient_instance.dob = dob
            patient_instance.save()
        if email not in [None,""]:
            patient_instance.email = email
            patient_instance.save()
        # if img not in [None,""]:
        #     patient_instance.img = img
        #     patient_instance.save()

        patient_serializer = PatientSerializer(patient_instance).data
        patient_serializer['selected'] = False

        if user.family_members==None:
            user.family_members=[patient_serializer]
        else:
            user.family_members.append(patient_serializer)
        
        user.save()

        return Response({
                "MSG":"SUCCESS",
                "ERR":None,
                "BODY":"Family member added successfully"
                    },status=status.HTTP_200_OK)

    def put(self,request):
        """
            API View to update the family member details
            With the given data a new user instance is created.

            Allowed Methods:
                -PUT
            
            Request data:
                id : [String,required] id of the new family member
                name:   [String] name of the patient
                email:  [String] email id of the patient
                aadhar: [String] aadhar number of the patient [*Optional]
                relation: [String] relation to the patient 
                gender: [String] gender of the patient
                blood :  [String] blood of the patient
                dob :  [String] dob of  the patient

            Authentication:
                -Required
                -UserAuthentication
        
        """

        user=request.user
        data=request.data
        id = data.get("id",None) #required
        name=data.get("name",None)     #required
        relation =data.get("relation",None) #required
        gender =data.get("gender",None)
        blood =data.get("blood",None)
        dob =data.get("dob",None)
        email=data.get("email",None)
        img =data.get("img",None)
        aadhar=data.get("aadhar",None) #optional

        if id in [None,""]:
            return display_response(
                msg = "FAILED",
                err = "Please provide valid id",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        if id == user.id:
            return display_response(
                msg = "FAILED",
                err = "You can update only your family members",
                body = None,
                statuscode = status.HTTP_406_NOT_ACCEPTABLE
            )

        """
            Checks if the user is already added to the family. Check if the user is already in User Instance.
            Update the user instance with the new data and the json_data in family member
        """

        get_user = Patient.objects.filter(id=id).first()
        if get_user is None:
            return display_response(
                msg = "FAILED",
                err = "Family member does not exist",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        for i in user.family_members:
            if i['id'] == id:
                """Update the values if they are not None"""
                if name not in [None,""]:
                    i['name'] = name
                    user.save()
                if email not in [None,""]:
                    i['email'] = email
                    user.save()
                if relation not in [None,""]:
                    i['relation'] = relation
                    user.save()
                if gender not in [None,""]:
                    i['gender'] = gender
                    user.save()
                if blood not in [None,""]:
                    i['blood'] = blood
                    user.save()
                if dob not in [None,""]:
                    i['dob'] = dob
                    user.save()
                if img not in [None,""]:
                    i['img'] = img
                    user.save()
                    

        if name not in [None,""]:
            get_user.name = name
            get_user.save()

        if email not in [None,""]:
            get_user.email = email
            get_user.save()
        
        if relation not in [None,""]:
            get_user.relation = relation
            get_user.save()

        if gender not in [None,""]:
            get_user.gender = gender
            get_user.save()

        if blood not in [None,""]:
            get_user.blood = blood
            get_user.save()

        if dob not in [None,""]:
            get_user.dob= dob
            get_user.save()

        if img not in [None,""]:
            get_user.img = img
            get_user.save()

        return display_response(
            msg = "SUCCESS",
            err = None,
            body = "Family member updated successfully",
            statuscode = status.HTTP_200_OK
        )
   
#---------Home Screen API --------------------
class HomeScreenAPI(APIView):
    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def convert_to_dBY(self,ymd):
        res = dtt.strptime(ymd,Ymd).strftime(dBY)
        return f"{res}"

    def get(self,request,format=None):
        
        """
            Home Screen API format.It has all the contents of the frontend ui based json fields.
            All are generated here in api json_data
        """
        user = request.user
        json_data =  {
            "user" : {},
            "firstcarousel" : {},
            "lastcarousel":{},
            "slider" : {
                "title" : "Best of Us",
                "content" : [],
                "isempty": True,
            },
            "categoryspecialist" : {
                "title" : "Our Doctors",
                "isempty" : True,
                "categories_1" : [],
                "categories_2" : [],
            }, 
            "promotiondeparts" : {
                "isempty" : True,
                "depts" : [],
            },
            "upcomingappointments" : {
                "isempty" : True,
                "appointments" : [],
            },
            "endcontent":{
                "building":"1",
                "doctors" : "50+",
                "patients" : "150+",
                "content" : "Our community of doctors and patients drive us to create technologies for better and afforable healthcare"
            }
        }

        """
            User Serializer to get the user details
        """
        user_serializer = UserSerializer(user,context={'request' :request})
        json_data['user'] = user_serializer.data
        """
            Getting all the Carousel models objects.
            Add the carousel which has id = 1 for first carousel and then id = 2 for second carousel.If it has None
            then add the default image and id
        """
        get_carousel = Carousel.objects.all()

        if get_carousel.count() > 0:
            carousel_serializer = CarouselSerializer(get_carousel,many=True,context={"request":request}).data
            json_data['firstcarousel'] = {
                    "id" : carousel_serializer[0]['id'],
                    "img" : carousel_serializer[0]['img']
                }
            if get_carousel.count() > 1:
                json_data['lastcarousel'] = {
                    "id" : carousel_serializer[1]['id'],
                    "img" : carousel_serializer[1]['img']
                }
            else:
                json_data['lastcarousel'] = {
                    "id" : "2",
                    "img" : LAST_CAROUSEL
                }     
        else:
            json_data['firstcarousel'] = {
                "id" : "1",
                "img" : FIRST_CAROUSEL
            }
            json_data['lastcarousel'] = {
                "id" : "2",
                "img" : LAST_CAROUSEL
            }   

        """
            Getting the promotional Slider Contents in a list format.
        """
        promotions = PromotionalSlider.objects.all()
        if len(promotions) > 0:
            promote_serial = PromotionalSliderSerializer(promotions,many=True,context={"request":request})
            json_data['slider']['isempty'] = False
            for i in promote_serial.data:
                data = {
                    "id" : i['id'],
                    "img" : i['img'],
                }
                json_data['slider']['content'].append(data)
        
        """
            categoryspecialist is the CategorySpecialist Model which conssit of all the categories and their specialists.  
        """
        categoryspecialist = CategorySpecialist.objects.all()
        if len(categoryspecialist) > 0:
            category_serial = CategorySpecialistSerializer(categoryspecialist,many=True,context={"request":request})
            json_data['categoryspecialist']['isempty'] = False
            for i in category_serial.data:
                data = {
                    "id" : i['id'],
                    "name" : i['name'],
                    "img" : i['img']
                }
                if len(categoryspecialist) < 8:
                    json_data['categoryspecialist']['categories_1'].append(data)
                else:
                    if i % 2 == 0:
                        json_data['categoryspecialist']['categories_2'].append(data)
                    else:
                        json_data['categoryspecialist']['categories_1'].append(data)
        """
            promotiondeparts consists of the departments of a particular categoryspecialist
        """
        promotiondeparts = CategoryPromotion.objects.all()
        if len(promotiondeparts) > 0:
            json_data['promotiondeparts']['isempty'] = False
            promote_serial = CategoryPromotionSerializer(promotiondeparts,many=True,context={"request":request})
            for i in promote_serial.data:
                categorydata = {
                    "id" : i['id'],
                    "title": i['title'],
                    "departments": [],
                }
                for j in i['category']['depts']:
                    deptdata = {
                        "id" : j['id'],
                        "name" : j['name'],
                        "img" : j['img'],
                    }
                    categorydata['departments'].append(deptdata)
                json_data['promotiondeparts']['depts'].append(categorydata)

        """
            Add the upcoming live appointments
        """
        patients_id = []
        patients_id.append(user.patientid)
        
        if (user.family_members != None):
            if len(user.family_members) > 0 :
                for mem in user.family_members:
                    patients_id.append(mem['id'])

        current_date = dtt.now(IST_TIMEZONE).strftime(Ymd)
        query = Appointment.objects.filter(patient_id__in = patients_id,closed=False,date__gte=current_date).order_by('-created_at').all()
        serializer = AppointmentSerializer(query,many=True,context={"request":request})

        for x in serializer.data:
            data = {
                "id" : x['id'],
                "img" : x['doctor']['profile_img'],
                "name" : x['doctor']['name'],
                "specialisation" : x['doctor']['specialisation'],
                "time" : self.convert_to_imp(x['time']),
                "date" : self.convert_to_dBY(x['date']),   
            }
            json_data['upcomingappointments']['appointments'].append(data)
        
        if len(json_data['upcomingappointments']['appointments']) > 0:
            json_data['upcomingappointments']['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---------All Categories Screen API --------------------
class CategoriesScreen(APIView):
    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def get(self,request,format=None):
        json_data = {
            "departments":{
                "title": "Know your specialists",
                "isempty": True,
                "content": [],
            },
            "specialist":{
                "title": "Search by specialists",
                "isempty": True,
                "content": [],
            },
        }

        """
            Getting all the departments and their respective categories.
        """
        departments = Department.objects.all()
        if len(departments) > 0:
            json_data['departments']['isempty'] = False
            dept_serial = DepartmentSerializer(departments,many=True,context={"request":request})
            for i in dept_serial.data:
                data = {
                    "id" : i['id'],
                    "name" : i['name'],
                    "img" : i['img'],
                }
                json_data['departments']['content'].append(data)


        specialists = CategorySpecialist.objects.all()
        if len(specialists) > 0:
            json_data['specialist']['isempty'] = False
            specialist_serial = CategorySpecialistSerializer(specialists,many=True,context={"request":request})
            for i in specialist_serial.data:
                data = {
                    "id" : i['id'],
                    "name" : i['name'],
                    "img" : i['img'],
                }
                json_data['specialist']['content'].append(data)

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---------Notifications Screen API --------------------
class PatientNotificationScreen(APIView):
    permission_classes = []
    authentication_classes=[UserAuthentication]

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
        patient = request.user
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
        query = PatientNotification.objects.filter(patientid=patient).order_by('-created_at')
        if len(query) > 0:
            json_data['isempty'] = False
            serializer = PatientNotificationSerializer(query,many=True,context={"request":request})
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

        patient = request.user
        
        query = PatientNotification.objects.filter(patientid__id=patient.id,id=notificationid).first()
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

#--------Doctors Details Display In Detail Screen API--------------------
class DoctorSlotDetails(APIView):
    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def get(self,request,format=None):
        """
            User is the current registered user.
            Doctor Id is the 'id' field of the doctor model whose details are to be displayed.
            ---------------------
            GET method:
                doctorid : [String,required] Id of the doctor
                querydate : [String,required] Date in the format 'dd-mm-yyyy'
        """

        json_data = {
            "dates" : [],
            "availabledates" : [],
            "selecteddate": "",
            "morning" : {
                "isempty" : True,
                "slots" : [],
            },
            "afternoon" :  {
                "isempty" : True,
                "slots" : [],
            },
            "evening" :  {
                "isempty" : True,
                "slots" : [],
            },
            "doctor" : {},
            "familymembers" : [],
            "selectedfamilymember" : {},
        }
        
        user = request.user

        doctorid = request.query_params.get('doctorid', None)
        querydate = request.query_params.get('querydate', None)
        if doctorid is None:
            return display_response(
                msg = "FAILURE",
                err= "Doctorid is required",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )
        

        doctor = Doctor.objects.filter(id=doctorid).first()
        if doctor is None:
            return display_response(
                msg = "FAILURE",
                err= "Doctor was not found",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        """
            Adding the doctor details to te json_data['doctor'] field
        """
        doc_serialize = DoctorSerializer(doctor,context={"request":request})  
        json_data['doctor'] = {
            "id" : doc_serialize.data['id'],
            "doctor_id" : doc_serialize.data['doctor_id'],
            "name" : doc_serialize.data['name'],
            "experience" : doc_serialize.data['experience'],
            "gender" : doc_serialize.data['gender'],
            "qualification" : doc_serialize.data['qualification'],
            "specialisation" : doc_serialize.data['specialisation'],
            "defaultimg" : doc_serialize.data['name'][0:1],
            "img" : doc_serialize.data['profile_img']
        }

        """
            Get all the family members of the requesting user.
            Appending the current user data details also
        """
        members = []
        user_mem = {
            "id" : user.patientid,
            "name" : user.name,
            "selected" : user.selected,
        }
        if user.selected == True:
            json_data['selectedfamilymember'] = user_mem
        members.append(user_mem)

        if user.family_members is not None:
            for i in user.family_members:
                mem = {
                    "id" : i['id'],
                    "name" : i['name'],
                    "selected" : i['selected'],
                }
                if i['selected'] == True:
                    json_data['selectedfamilymember'] = mem
                members.append(mem)    

        json_data['familymembers'] = members
        
        timings = DoctorTimings.objects.filter(doctor_id=doctor).first() 
        timings_serializer = DoctorTimingsSerializer(timings,context={'request' :request}).data
        dates_arr = []
        print("----------------------")
        print(timings)
        if timings is not None:
            for j in timings.availability['dates_arr']:
                if (dtt.strptime(j, "%m/%d/%Y").strftime(Ymd)) >=  dtt.now(IST_TIMEZONE).strftime(Ymd):
                    dt_1 = dtt.strptime(j, "%m/%d/%Y").strftime(dmY)
                    day_ = dtt.strptime(j, "%m/%d/%Y").weekday()
                    dt_2 = dtt.strptime(j, "%m/%d/%Y").strftime("%d")
                    data = {
                        "date" : dt_1,
                        "day" : calendar.day_name[day_],
                        "date_num" : dt_2
                    }
                    json_data['availabledates'].append(data)
                    dates_arr.append(dt_1)
            json_data['dates'] = dates_arr
        else:
            print(json_data)
            return display_response(
                msg = "SUCCESS",
                err= "No dates available",
                body = json_data,
                statuscode = status.HTTP_200_OK
            )            

        if len(dates_arr) == 0:
            print(json_data)
            return display_response(
                msg = "SUCCESS",
                err= "No dates available",
                body = json_data,
                statuscode = status.HTTP_200_OK
            ) 

        if querydate in [None,""]:
            querydate = dtt.strptime(dates_arr[0],dmY).strftime("%m/%d/%Y")
            json_data['selecteddate'] = dates_arr[0]
        else:
            if querydate not in dates_arr:
                return display_response(
                    msg = "FAILURE",
                    err= "Date is not available",
                    body = None,
                    statuscode = status.HTTP_400_BAD_REQUEST
                )
            else:
                json_data['selecteddate'] = querydate
                querydate = dtt.strptime(querydate,dmY).strftime("%m/%d/%Y")



        """
            Get the slots for morning.
            "morning" : {
                "isempty" : True,
                "slots" : [],
            },
            Inside slots ,the format is 
            if(available == true) data = {
                "date" : "d-m-y",
                "count" : "count"
            }
        """

        mrngarr = timings.timeslots[querydate]['morning'] 
        morning_slots = mrngarr.keys()

        for x in morning_slots:
            if mrngarr[x]['available'] == True:
                data = {
                    "date" : dtt.strptime(x, HMS).strftime(IMp),
                    "count" : mrngarr[x]['count']
                }
                json_data['morning']['slots'].append(data)
        if len(json_data['morning']['slots']) > 0:
            json_data['morning']['isempty'] = False

        """
            Get the slots for afternoon.
            "afternoon" : {
                "isempty" : True,
                "slots" : [],
            },
            Inside slots ,the format is 
            if(available == true) data = {
                "date" : "d-m-y",
                "count" : "count"
            }
        """

        noonarr = timings.timeslots[querydate]['afternoon'] 
        noon_slots = noonarr.keys()
        
        for y in noon_slots:
            if noonarr[y]['available'] == True:
                data = {
                    "date" : dtt.strptime(y,HMS).strftime(IMp),
                    "count" : noonarr[y]['count']
                }
                json_data['afternoon']['slots'].append(data)
                
        if len(json_data['afternoon']['slots']) > 0:
            json_data['afternoon']['isempty'] = False
 
        """
            Get the slots for afternoon.
            "evening" : {
                "isempty" : True,
                "slots" : [],
            },
            Inside slots ,the format is 
            if(available == true) data = {
                "date" : "d-m-y",
                "count" : "count"
            }
        """       
        eveningarr = timings.timeslots[querydate]['evening'] 
        evening_slots = eveningarr.keys()
        for z in evening_slots:
            if eveningarr[z]['available'] == True:
                data = {
                    "date" : dtt.strptime(z,HMS).strftime(IMp),
                    "count" : eveningarr[z]['count']
                }
                json_data['evening']['slots'].append(data)
                
        if len(json_data['evening']['slots']) > 0:
            json_data['evening']['isempty'] = False

        print(json_data)
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )


#--------Updating the selected member for the user appointment booking--------
class BookingChangeMember(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def put(self,request):
        """
            This put method is responsible for updating the selected user member during the booking.
            Default is the registered user given as selected="True" and if u want to change the booking for 
            the different family members,then use this method.

            PUT method:
                memberid :[String,required] id of the member to be selected
        """
        user = request.user
        memberid = request.data.get('memberid', None)
        print(memberid)
        if memberid is None:
            return display_response(
                msg = "FAILURE",
                err= "Memberid is required",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        """
            Checking if the memberid is valid or not and if the memberid is present in the family members list
        """
        get_member = Patient.objects.filter(id=str(memberid)).first()
        print(get_member)
        if get_member is None:
            return display_response(
                msg = "FAILURE",
                err= "Memberid is invalid",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        if user.patientid == memberid:
            """
                Selected user is the USER model instance person.
                Then updated user.selected = True and other family_members selected = False
            """
            user.selected = True
            for i in user.family_members:
                if i['selected'] == True:
                    i['selected'] = False
            user.save()   
        else:
            """
                Selected user is the FAMILY member
                Then updated user.selected = False and other family_members selected = False and selected family member as True
            """
            user.selected = False
            for i in user.family_members:
                if i['id'] == memberid:
                    i['selected'] = True
                else:
                    if i['selected'] == True:
                        i['selected'] = False
            user.save()
        
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = None,
            statuscode = status.HTTP_200_OK
        )

#-------Search Screen API--------------------
class SearchResults(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request,format=None):
        """
            If this is default search or first search then display only that results without any filter options
            GET method:
                search_type :[String,required] search_type can be either "default" or "first"
                query : [String(query),required] Previous query searched by the user.        
        ----------------------------------------------------------
            Filtering of doctors data.
            GET method:
                query : [String(query),required] Previous query searched by the user.
                specialist : [String(id),optional] Specialist of the doctor will be filtered from the resulted doctors
                exp : [int(customid),optional] Experience of the doctor will be filtered from the resulted doctors
                    1 - Relevance
                    2 - Low to high
                    3 - High to low
                gender : [String(customid),optional] Gender of the doctor will be filtered from the result of the search
                    A - All 
                    M - Male
                    F - Female
        ----------------------------------------------
        """

        json_data = {
            "isempty" : True,
            'doctors' : [],
            'specialisation':[],
            'gender' : {
                "selected_id" : "A",
                "gender" : [
                    {
                    "id" : "A",
                    "title" : "All",
                    "selected" : True,
                    },
                    {
                    "id" : "M",
                    "title" : "Male",
                    "selected" : False,
                    },
                    {
                    "id" : "F",
                    "title" : "Female",
                    "selected" : False,
                    }
                
            ]
            },
            'experience': {
                "selected_id" : 1,
                "experience" : [
                {
                    "id" : 1,
                    "title" : "Relevance",
                    "selected" : True,
                },
                {
                    "id" : 2,
                    "title" : "Low to High",
                    "selected" : False,
                },
                {
                    "id" :3,
                    "title" : "High to Low",
                    "selected" : False,
                }
            ],
            }
        }

        user = request.user
        data = request.query_params
        query = data.get('query', "")
        search_type = data.get("search_type","first")
        specialist = data.get('specialist', None)
        exp = data.get('exp', 1)
        gender = data.get('gender','A')

        """
            Search for doctors in their names and their department wise
        """
        temp = []


        name_set = Doctor.objects.filter(Q(name__contains=query) , is_blocked=False)
        name_serializer = DoctorSerializer(name_set,many=True,context={"request":request})
        for i in name_serializer.data:
            data = {
                "id" : i['id'],
                "doctor_id" : i['doctor_id'],
                "name" : i['name'],
                "profile_img" : f"{i['profile_img']}",
                "experience" : i['experience'],
                "gender" : i['gender'],
                "deptid" : i['department_id']['id'],
                "deptname" : i['department_id']['name'],
            }
            temp.append(data)
            print(f"--------------------{i['name']}--------------------")


        dept_set = Department.objects.filter(Q(name__icontains=query))
        dept_serializer = DepartmentSerializer(dept_set,many=True,context={"request":request})
        for j in dept_serializer.data:
            queryset = Doctor.objects.filter(department_id__id=j['id'],is_blocked=False).all()
            queryset_serializer = DoctorSerializer(queryset,many=True,context={"request":request})
            for x in queryset_serializer.data:
                data = {
                    "id" : x['id'],
                    "doctor_id" : x['doctor_id'],
                    "name" : x['name'],
                    "profile_img" : f"{x['profile_img']}",
                    "experience" : x['experience'],
                    "gender" : x['gender'],
                    "deptid" : x['department_id']['id'],
                    "deptname" : x['department_id']['name'],
                }
                temp.append(data)

        category_set = CategorySpecialist.objects.filter(Q(name__icontains=query))
        category_serializer = CategorySpecialistSerializer(category_set,many=True,context={"request":request})
        for k in category_serializer.data:
            depts_id_list = [x['id'] for x in k['depts']]
            queryset = Doctor.objects.filter(department_id__id__in=depts_id_list,is_blocked=False).all()
            queryset_serializer = DoctorSerializer(queryset,many=True,context={"request":request})
            for y in queryset_serializer.data:
                data = {
                    "id" : y['id'],
                    "doctor_id" : y['doctor_id'],
                    "name" : y['name'],
                    "profile_img" : f"{y['profile_img']}",
                    "experience" : y['experience'],
                    "gender" : y['gender'],
                    "deptid" : y['department_id']['id'],
                    "deptname" : y['department_id']['name'],
                }
                temp.append(data)

        print("----doctor set-----")
        print(name_set)
        print(dept_set)
        print(category_set)

        final = []
        for a in temp:
            id_ = list(set([x['id'] for x in final])) 
            if a['id'] not in id_:
                final.append(a)

        json_data['doctors'] = final

        get_specialisation = Department.objects.all()
        get_specialisation_serializer = DepartmentSerializer(get_specialisation,many=True,context={"request":request})
        for l in get_specialisation_serializer.data:
            data = {
                "id" : l['id'],
                "title" : l['name'],
                "selected" : False,
            }
            json_data['specialisation'].append(data)


        if search_type == "first":
            if len(json_data['doctors']) > 0:
                json_data['isempty'] = False
            return display_response(
                msg = "SUCCESS",
                err= None,
                body = json_data,
                statuscode = status.HTTP_200_OK
            )
        else:
            """
                Gender : Filtering the gender of the doctor based on the request 
                A - All
                M - Male
                F - Female
            """
            initial = json_data['doctors']
            filter_1 = [] #Filtered data after gender 
            if gender not in [None,""]:
                if gender == "M":
                    for m in initial:
                        if m['gender'] == 'M':
                            filter_1.append(m)
                    for g in json_data['gender']['gender']:
                        if g['id'] == 'M':
                            json_data['gender']['selected_id'] = g['id']
                            g['selected'] = True
                        else:
                            g['selected'] = False
                elif gender=="F":
                    for f in initial:
                        if f['gender'] == 'F':
                            filter_1.append(f)
                    for g in json_data['gender']['gender']:
                        if g['id'] == 'F':
                            json_data['gender']['selected_id'] = g['id']
                            g['selected'] = True
                        else:
                            g['selected'] = False
                else:
                    filter_1 = initial
                    for g in json_data['gender']['gender']:
                        if g['id'] == 'A':
                            json_data['gender']['selected_id'] = g['id']
                            g['selected'] = True
                        else:
                            g['selected'] = False


            """
                Experience : Filtering the doctor based on experience
                1 - Relevance
                2 - Low to high
                3 - High to low
            """  
            if exp not in [None,""]:
                exp = int(exp)
                if exp == 2:
                    filter_1.sort(key=lambda e: e['experience'], reverse=False)
                    for e in json_data['experience']['experience']:
                        if e['id'] == 2:
                            json_data['experience']['selected_id'] = e['id']
                            e['selected'] = True
                        else:
                            e['selected'] = False
                elif exp == 3:
                    filter_1.sort(key=lambda e: e['experience'], reverse=True)
                    for e in json_data['experience']['experience']:
                        if e['id'] == 3:
                            json_data['experience']['selected_id'] = e['id']
                            e['selected'] = True
                        else:
                            e['selected'] = False
                else:
                    for e in json_data['experience']['experience']:
                        if e['id'] == 1:
                            json_data['experience']['selected_id'] = e['id']
                            e['selected'] = True
                        else:
                            e['selected'] = False

            """
                Specialist : Filtering the doctor based on specialist
                specialist: [String(id)] is required and get department object from that
            """
            filter_2 = [] #Filtered data after specialist
            if specialist not in [None,""]:
                get_spec = Department.objects.filter(id=specialist).first()
                for doc in filter_1:
                    if doc['deptid'] == get_spec.id:
                        filter_2.append(doc)
                for s in json_data['specialisation']:
                    if s['id'] == get_spec.id:
                        s['selected'] = True
                    else:
                        s['selected'] = False
            else:
                filter_2 = filter_1      
                for s in json_data['specialisation']:
                    s['selected'] = False        

            json_data['doctors'] = filter_2
            if len(json_data['doctors']) > 0:
                json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#-------Appointment History --------------------------------
class AppointmentHistory(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def convert_to_dBY(self,ymd):
        res = dtt.strptime(ymd,Ymd).strftime(dBY)
        return f"{res}"

    def get(self, request,format=None):
        json_data = {
            "isempty" : True,
            "appointments" : [],
        }
        user = request.user

        patients_id = []
        patients_id.append(user.patientid)
        for mem in user.family_members:
            patients_id.append(mem['id'])

        query = Appointment.objects.filter(patient_id__in=patients_id,closed=True).order_by('-created_at').all()
        serializer = AppointmentSerializer(query,many=True,context={"request":request})
        for x in serializer.data:
            data = {
                "id" : x['id'],
                "img" : x['doctor']['profile_img'],
                "name" : x['doctor']['name'],
                "defaultimg" : x['doctor']['name'][0:1],
                "specialisation" : x['doctor']['specialisation'],
                "time" : self.convert_to_imp(x['time']),
                "date" : self.convert_to_dBY(x['date']),   
            }
            json_data['appointments'].append(data)
        
        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        
        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#-------Pending Appointment -------------------------------
class PendingAppointment(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def convert_to_dBY(self,ymd):
        res = dtt.strptime(ymd,Ymd).strftime(dBY)
        return f"{res}"

    def get(self, request,format=None):
        """
            this view is responsible for getting the pending appointments.
            maintains two types of appointments for live and upcoming.
            GET method:
                type : [int(id),required] Search type in query_params
                    - 1 : Live appointments
                    - 2 : Upcoming appointments
        """
        json_data = {
            "type" : None,
            "isempty" : True,
            "appointments" : [],
        }
        user = request.user
        search_type = int(request.query_params.get('type',1))
        current_date = dtt.now(IST_TIMEZONE).strftime(Ymd)

        patients_id = []
        patients_id.append(user.patientid)

        if user.family_members is not None:
            for mem in user.family_members:
                patients_id.append(mem['id'])
    
        if search_type == 1:
            query = Appointment.objects.filter(patient_id__in = patients_id,closed=False,date=current_date).order_by('-created_at').all()
        else:
            query = Appointment.objects.filter(patient_id__in = patients_id,closed=False,date__gt=current_date).order_by('-created_at').all()
        
        serializer = AppointmentSerializer(query,many=True,context={"request":request})
        for x in serializer.data:
            data = {
                "id" : x["id"],
                "img" : x['doctor']['profile_img'],
                "name" : x['doctor']['name'],
                "defaultimg" : x['doctor']['name'][0:1],
                "specialisation" : x['doctor']['specialisation'],
                "time" : self.convert_to_imp(x['time']),
                "date" : self.convert_to_dBY(x['date']),   
            }
            json_data['appointments'].append(data)
        
        if len(json_data['appointments']) > 0:
            json_data['isempty'] = False
        json_data['type'] = f"{search_type}"

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#-------AppointmentInDetails --------------------------------
class AppointmentInDetail(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def convert_to_imp(self,hms):
        imp = dtt.strptime(hms,HMS).strftime(IMp)
        return f"{imp}"

    def get(self, request,format=None):

        json_data = {
            "appointmentid" : "",
            "status" : "Pending",
            "details" : [],
            "timeline" : {},
            "doctor" : {},
            "patient" : {},
            "counter" :{},
            "measures" :MEASURES_TO_BE_TAKEN,
            "enablecancel" : True,

        }
        user = request.user
        appointment_id = request.query_params.get('appointmentid',None)

        if appointment_id in [None,""]:
            return display_response(
                msg = "FAILURE",
                err= "Appointment id is required",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        appointment = Appointment.objects.filter(id=appointment_id).first()
        if appointment is None:
            return display_response(
                msg = "FAILURE",
                err= "Appointment not found",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )
        serializer = AppointmentSerializer(appointment,context={"request":request}).data
        
        """
            Updating the appointment id.Updating the status based on the appointment status.
        """
        json_data['appointmentid'] = serializer['id']
        if serializer['closed'] == True:
            if serializer['consulted'] == True:
                json_data['status'] = "Completed"
            else:
                json_data['status'] = "Missed"
        else:
            """
                Check in timeline and update the status as processing or pending
            """
            if serializer['timeline']['step2']['completed'] == True:
                json_data['status'] = "Processing"
            else:
                json_data['status'] = "Pending"

        """
            Adding the appointment date,time,venue,consultation type.
            if closed != True:
                Add the estimated arrival for the appointment.
        """
        time_format = dtt.strptime(serializer['time'],HMS).strftime(IMp)
        date_format = dtt.strptime(serializer['date'],Ymd).strftime(dmY)
        details_data = [
            {
                "title": "Venue",
                "subtitle" : "Sri Ramachandra Medical Hospital Hospital",
            },
            {
                "title": "Date & Time",
                "subtitle" : f"{date_format} , {time_format}",
            },
            {
                "title": "Consultation",
                "subtitle" : "In Visit",
            },
            {
                'title': "Location",
                "subtitle" : SRMC_LOC_URL,
            }
        ]
        json_data['details'] = details_data

        if serializer['closed'] == False:
            est_data = {
                "title" : "Estimated Arrival",
                "subtitle" : "",
            }
            diff_1 = dtt.strptime(serializer['time'],HMS) - timedelta(minutes=20)
            time_format_1 = diff_1.strftime(IMp)
            diff_2 = dtt.strptime(serializer['time'],HMS) - timedelta(minutes=15)
            time_format_2 = diff_2.strftime(IMp)
            est_data['subtitle'] = f"{time_format_1} - {time_format_2}"
            json_data['details'].append(est_data)
        """
            Updating the timeline data.Converting HMS into IMP format.
        """    
        json_data['timeline'] = serializer['timeline']
        json_data['timeline']['cancelled'] = serializer['cancelled']
        step1 = json_data['timeline']['step1']
        step2 = json_data['timeline']['step2']
        step3 = json_data['timeline']['step3']
        stepcancel = json_data['timeline']['cancel']
        if step1['completed'] == True:
            step1['time'] = self.convert_to_imp(step1['time'])
        else:
            step1['time'] = "00:00"
        
        if step2['completed'] == True:
            step2['time'] = self.convert_to_imp(step2['time'])
        else:
            step2['time'] = "00:00"
        
        if step3['completed'] == True:
            step3['time'] = self.convert_to_imp(step3['time'])
        else:
            step3['time'] = "00:00"
        
        if stepcancel['completed'] == True:
            stepcancel['time'] = self.convert_to_imp(stepcancel['time'])
        else:
            stepcancel['time'] = "00:00"
    


        """
            Updating the doctor data.
        """
        doctor_data = {
            "img" : serializer['doctor']['profile_img'],
            "name" : serializer['doctor']['name'],
            "defaultimg" : serializer['doctor']['name'][0:1],
            "qualification" : f"{serializer['doctor']['qualification']} | {serializer['doctor']['specialisation']}",
            "gender" : "Male" if serializer['doctor']['gender'] == 'M' else "Female" if serializer['doctor']['gender'] == "F" else "Other",
        }
        json_data['doctor'] = doctor_data

        """
            Updating the patient details
        """
        patient_data = {
            "id" : serializer['patient']['id'],
            "name" : serializer['patient']['name'],
            "defaultimg" : serializer['patient']['name'][0:1],
            "email" : serializer['patient']['email'],
            "relation" : serializer['patient']['relation'],
            "mobile" : user.mobile
        }
        json_data['patient'] = patient_data

        """
            Add the counter details to the json_data
            format : {
                "info" : COUNTER_INFO,
                "counters" : {
                    "counter" : "counter1",
                    "location" : "firstfloor | right side to main entrance"
                }
            }
        """
        counter_json = {
            "info" : SERVICE_COUNTER_INFO,
            "availablecounter" : [],
        }
        for n in appointment.counter:
            _data = {
                "id" : n['id'],
                "counter" : f"{n['counter']} at Floor:{n['floor']}",
            }
            counter_json['availablecounter'].append(_data)
        json_data['counter'] = counter_json


        """
            If closed = False then  enablecancel=True.
        """
        if serializer['closed'] == True:
            json_data['enablecancel'] = False


        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#------Appointment Booking----------
class BookAppoinment(APIView):

    authentication_classes=[UserAuthentication]
    permission_classes=[]
    """
        API to book appoinment
        Allowed methods:
            -POST
        
        Authentication: Required UserAuthentication

        POST:
            data:
                patient_id: [string,required] id of the patient
                date:       [string,required,format: mm/dd/yyyy] date of appoinment
                time:       [string,required,format: hh:mm:ss] time for the appoinment
                doctor_id:  [ string,required] id of the doctor

    """
    
    def post(self,request,format=None):
        
        data=self.request.data

        patiend_id=data.get("patient_id")
        date=data.get("date")
        time=data.get("time")
        doctor_id=data.get("doctor_id")

        print(data)

        validation_arr=["",None]
        
        """validate data"""
        if patiend_id in validation_arr or date in validation_arr or time in validation_arr or doctor_id in validation_arr:
            return Response({
                    "MSG":"FAILED",
                    "ERR":"Invalid data given",
                    "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dataout = make_appointment_booking(
                patient_id_= patiend_id,
                date_= date,
                time_= time,
                doctor_id_= doctor_id
            )
            return display_response(
                msg = dataout['MSG'],
                err= dataout['ERR'],
                body = dataout['BODY'],
                statuscode = dataout['STATUS'],
            )
        except Exception as e:
            return Response({
                        "MSG":"ERROR",
                        "ERR":str(e),
                        "BODY":"Failed outside of exception in booking"
                                },status=status.HTTP_200_OK)

#-----Confirmation Screen API-----
class ConfirmationScreen(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        json_data = {
            "details" : [],
            "selecteddate" : "",
            "selectedtime" : "",
            "doctor" : {},
            "patient" : {},
            "measures" : MEASURES_TO_BE_TAKEN,
            "changemember" : CHANGE_MEMBER_INFO
        }
        user = request.user
        data = request.query_params

        date = data.get("date",None)
        time = data.get("time",None)
        patientid = data.get("patientid",None)
        doctorid = data.get("doctorid",None)


        if patientid in [None,""] or doctorid in [None,""] or date  in [None,""] or time in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        """
            Adding the patient and doctor information and details of appoinment
        """
        patient = Patient.objects.filter(id=patientid).first()
        patient_data = {
            "id" : f"{patient.id}",
            "name" : f"{patient.name}",
            "img" : f"{patient.img}",
            "defaultimg" : f"{patient.name[0:1]}",
            "email" : f"{patient.email}",
            "relation" : f"{patient.relation}",
            "mobile" : f"{user.mobile}"
        }
        json_data['patient'] = patient_data

        doctor = Doctor.objects.filter(id=doctorid).first()
        doctor_data = {
            "id":doctor.id,
            "img" : f"{doctor.profile_img}",
            "defaultimg": f"{doctor.name[0:1]}",
            "name" : f"{doctor.name}",
            "qualification" : f"{doctor.qualification} | {doctor.specialisation}",
            "gender" : "Male" if doctor.gender == 'M' else "Female" if doctor.gender == "F" else "Other",
        }
        json_data['doctor'] = doctor_data

        if date not in [None , ""]:
            date_format = dtt.strptime(date,dmY).strftime(dBY)
            json_data['selecteddate'] = dtt.strptime(date,dmY).strftime("%m/%d/%Y")
        
        if time not in [None , ""]:
            time_format = dtt.strptime(time,IMp).strftime(HMS)
            json_data['selectedtime'] = time_format

        details_data = [
            {
                "title": "Venue",
                "subtitle" : "Sri Ramachandra Medical Hospital Hospital",
            },
            {
                "title": "Date & Time",
                "subtitle" : f"{date_format} , {time}",
            },
            {
                "title": "Consultation",
                "subtitle" : "In Visit",
            }
        ]
        json_data['details'] = details_data

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#----Raise Tickets API-----
class PatientTicketsIssues(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def post(self,request):
        user = request.user
        data = request.data
        appointmentid = data.get('appointmentid', None)
        title = data.get("title",None)
        description = data.get("description",None)

        if title in [None,""] or description in [None,""] or appointmentid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        """
            Populate Ticket model
        """
        get_appointment = Appointment.objects.filter(id=appointmentid).first()
        get_doctor = Doctor.objects.filter(id=get_appointment.doctor_id).first()
        get_dept = Department.objects.filter(id=get_doctor.department_id.id).first()

        data = {
            "title" : title,
            "description" : description,
        }
        PatientTickets.objects.create(
            user_id = user,
            dept = get_dept,
            issues = data
        )
        return display_response(
            msg="SUCCESS",
            err=None,
            body=None,
            statuscode=status.HTTP_200_OK
        )

    def get(self , request , format=None):
        json_data = {
            "isempty" : True,
            "tickets" : [],
        }

        user = request.user

        tickets = PatientTickets.objects.filter(user_id=user).order_by("-created_at")
        serializer = PatientTicketsSerializer(tickets,many=True,context={"request":request}).data
        for i in serializer:
            data = {
                "id": i['id'],
                "closed" : i['closed'],
                "issues" : i['issues'],
                "created_at" : dtt.strptime(i['created_at'],YmdTHMSfz).strftime(dBYIMp),
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


#------medical Records Screen API -----
class FamilyMedicalRecord(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        json_data = {
            "isempty": True,
            "members" : [], 
        } 

        user = request.user
        serializer=UserSerializer(user).data
        
        user_data = {
            "patientid" : serializer['patientid'],
            "name" : serializer['name'],
            "img" : serializer['img'],
            "relation" : "Myself"
        }
        json_data['members'].append(user_data)

        if user.family_members is not None:
            for i in user.family_members:
                data = {
                    "patientid" : f"{i['id']}",
                    "name" : f"{i['name']}",
                    "img" : f"{i['img']}",
                    "relation" : f"{i['relation']}"
                }
                json_data['members'].append(data)

        if len(json_data['members']) > 0:
            json_data['isempty'] = False


        return display_response(
            msg = "SUCCESS",
            err = None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#----procedural records API -----
class PatientProceduralRecord(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        json_data = {
            "isempty": True,
            "patientid" : "",
            "procedures" : [],
        }
        patientid = request.query_params.get('patientid',None)
        print(patientid)
        if patientid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        json_data['patientid'] = patientid

        all_depts = Department.objects.all()

        procedures = MedicalRecords.objects.filter(patientid=patientid).order_by("-created_at")
        serializer = MedicalRecordsSerializer(procedures,many=True,context={"request":request}).data
        for i in serializer:
            created_by = Doctor.objects.filter(id=i['created_by']).first()  
            data = {
                "id": i['id'],
                "title" : i['title'],
                "created_by" : f"Dr. {created_by.name}" if created_by != None else None,
                "patientid" : f"{i['patientid']}",
                "created_at" : dtt.strptime(i['created_at'],YmdTHMSfz).strftime(dBYIMp),
                "dept" : []
            }
            for x in i['records']:
                dept_data = {
                    "deptid" : x['deptid'],
                    "deptname" : x['deptname'],
                    "deptimg" : "",
                    "created_at" : dtt.strptime(x['created_at'],YmdHMSfz).strftime(dBYIMp)
                }
                get_dept = all_depts.filter(id=x['deptid']).first()
                if get_dept is not None:
                    dept_data['deptimg'] = f"{get_dept.img}"
                data['dept'].append(dept_data)
            json_data['procedures'].append(data)

        if len(json_data['procedures']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )

#----Display medical Records-----
class DisplayMedicalRecords(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        
        json_data = {
            "isempty": True,
            "recordid" : "",
            "deptid" : "",
            "records" : [],
        }
        
        data = request.query_params
        recordid = data.get('recordid',None)
        deptid = data.get('deptid',None)

        if recordid in [None,""] or deptid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )
        
        medicalrecord = MedicalRecords.objects.filter(id=recordid).first()
        is_dept_index = 0


        for x in medicalrecord.records:
            if x['deptid'] == deptid:
                is_dept_index = medicalrecord.records.index(x)
                break
        
        for i in medicalrecord.records[is_dept_index]['records']:
            data = {
                "appointmentid" : i['appointmentid'],
                "doctorname" : i['doctorname'],
                "created_at" : dtt.strptime(i['created_at'],YmdHMSfz).strftime(dBYIMp),
                "date" : dtt.strptime(i['date'],Ymd).strftime(dBY),
            }
            json_data['records'].append(data)
        
        if len(json_data['records']) > 0:
            json_data['isempty'] = False

        json_data['recordid'] = recordid
        json_data['deptid'] = deptid

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )


#----Display Particular Appointment medical Records-----
class DisplayAppointmentMedicalRecords(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        
        json_data = {
            "isempty": True,
            "recordid" : "",
            "deptid" : "",
            "aid" : "",
            "date" : "",
            "time" :"",
            "doctor" : {},
            "records" : [],
        }
        
        data = request.query_params
        recordid = data.get('recordid',None)
        deptid = data.get('deptid',None)
        aid = data.get('aid',None)

        if recordid in [None,""] or deptid in [None,""] or aid in [None,""]:
            return display_response(
                msg="FAILED",
                err="Invalid data given",
                body=None,
                statuscode=status.HTTP_400_BAD_REQUEST
            )

        get_appointment = Appointment.objects.filter(id=aid).first()
        if get_appointment is not None:
            json_data['date'] = dtt.strptime(str(get_appointment.date),Ymd).strftime(dBY)
            json_data['time'] = dtt.strptime(str(get_appointment.time),HMS).strftime(IMp)
            json_data['doctor'] = {
                "name" : f"{get_appointment.doctor['name']}",
                "qualification" : f"{get_appointment.doctor['qualification']}",
                "specialisation" : f"{get_appointment.doctor['specialisation']}",
                "img" : f"{get_appointment.doctor['profile_img']}",
                "gender" : f"{get_appointment.doctor['gender']}",
            }

        medicalrecord = MedicalRecords.objects.filter(id=recordid).first()
        is_dept_index = 0

        for x in medicalrecord.records:
            if x['deptid'] == deptid:
                is_dept_index = medicalrecord.records.index(x)
                break
        
        for i in medicalrecord.records[is_dept_index]['records']:
            if aid == i['appointmentid']:
                data = {
                    "appointmentid" : i['appointmentid'],
                    "doctorname" : i['doctorname'],
                    "created_at" : dtt.strptime(i['created_at'],YmdHMSfz).strftime(dBYIMp),
                    "date" : dtt.strptime(i['date'],Ymd).strftime(dBY),
                    "files" : []
                }
                for j in i['files']:
                    data['files'].append({
                        "type" : j['type'],
                        "url" : j['url'],
                        "title" : j['name'],
                        "username" : j['username'],
                        "user" : j['user'],
                        "userid" : j['userid'],
                        "created_at" : dtt.strptime(j['created_at'],YmdHMSfz).strftime(dBYIMp)
                    })
                    json_data['records'] = data
                break
        
        if len(json_data['records']) > 0:
            json_data['isempty'] = False

        json_data['recordid'] = recordid
        json_data['deptid'] = deptid
        json_data['aid'] = aid

        return display_response(
            msg="SUCCESS",
            err=None,
            body=json_data,
            statuscode=status.HTTP_200_OK
        )


#---Cancel Single Appointment
class AppointmentCancel(APIView):
    authentication_classes = [UserAuthentication]
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

        user_serializer = UserSerializer(request.user,context={'request' :request}).data

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
            pat_msg = f"Your appointment {query.id} has been cancelled by you."
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

