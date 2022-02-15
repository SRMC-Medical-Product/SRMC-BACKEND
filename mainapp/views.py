"""
    File with all API's relating to the patient app

"""
from operator import ge
import re
from traceback import print_tb
from django.shortcuts import render
from django.utils import timezone

from datetime import datetime as dtt,time,date,timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from myproject.responsecode import display_response

from .models import *
from .auth import *
from .serializers import *
from mainapp.doctor_serializers import *
from .tasks import test_func
from .utils import dmY,Ymd,IMp,HMS,YmdHMS,dmYHMS,YmdTHMSf,YmdHMSf,mdY,IST_TIMEZONE,YmdTHMSfz

#------Profile Lists
REALTION = ["Father","Mother","Brother","Sister","Husband","Wife","Son","Daughter","Grandfather","Grandmother","Grandson","Granddaughter","Friend","Other"]
GENDER = ["Male","Female","Other"]
BLOOD = ["A+","A-","B+","B-","O+","O-","AB+","AB-"]

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
        
        if user_otp_instance.expiry_time<=timezone.now():
            user_otp_instance.delete()
        
        user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]

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



        #gets the userinstance in case of old user or creates a new user instance        
        user_instance=User.objects.filter(mobile=number).first()
        if user_instance is not None:
            return display_response(
                msg="FAIL",
                err="User already exist.Try signin",
                body=None,
                statuscode=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        patient_instance=Patient.objects.create(name=name,primary=True)
        user_instance=User.objects.get_or_create(mobile=number,name=name,patientid=patient_instance.id)[0]
        user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]
        
        if user_otp_instance.expiry_time<=timezone.now():
            user_otp_instance.delete()
        
        user_otp_instance=UserOtp.objects.get_or_create(user=user_instance)[0]

        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":{
                        "otp":user_otp_instance.otp,
                        "code":user_otp_instance.code
                            }
                        },status=status.HTTP_200_OK)

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
        json_data = {
            "profile" : {},
            "relation" : REALTION,
            "gender" : GENDER,
            "blood" : BLOOD,
        }
        query = Patient.objects.filter(id=request.user.patientid).first()
        serializer=PatientSerializer(query,context={"request":request})
        json_data['profile']=serializer.data
        test_func.delay()
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":json_data
                        },status=status.HTTP_200_OK)
    
    def put(self,request):
        user=request.user
        data=request.data
        name=data.get("name",None)     
        relation =data.get("relation",None) 
        gender =data.get("gender",None)
        blood =data.get("blood",None)
        dob =data.get("dob",None)
        email=data.get("email",None)
        aadhar=data.get("aadhar",None) #optional              
        
        patient = Patient.objects.filter(id=user.patientid).first()
        if patient is None:
            return display_response(
                msg="FAIL",
                err="User does not exist",
                body=None,
                statuscode=status.HTTP_406_NOT_ACCEPTABLE
            )
        if name not in [None,""]:
            patient.name=name
            user.name=name
            patient.save()
            user.save()

        if email not in [None,""]:
            patient.email = email
            patient.save()
        
        if relation not in [None,""]:
            patient.relation = relation
            patient.save()

        if gender not in [None,""]:
            patient.gender = gender
            patient.save()

        if blood not in [None,""]:
            patient.blood = blood
            patient.save()

        if dob not in [None,""]:
            patient.dob= dob
            patient.save()
        
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
            primary=False
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

        return display_response(
            msg = "SUCCESS",
            err = None,
            body = "Family member updated successfully",
            statuscode = status.HTTP_200_OK
        )
   
#---------Home Screen API --------------------
class HomeScreenAPI(APIView):
    authentication_classes=[]
    permission_classes=[]

    def get(self,request,format=None):
        
        """
            Home Screen API format.It has all the contents of the frontend ui based json fields.
            All are generated here in api json_data
        """

        json_data =  {
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
                "categories" : [],
            }, 
            "promotiondeparts" : {
                "isempty" : True,
                "depts" : [],
            },
            "upcomingappointments" : [], #TODO : Add the upcomingappointments
            "endcontent":{
                "building":"1",
                "doctors" : "50+",
                "patients" : "150+"
            }
        }


        """
            Getting all the Carousel models objects.
            Add the carousel which has id = 1 for first carousel and then id = 2 for second carousel.If it has None
            then add the default image and id
        """
        get_carousel = Carousel.objects.all()
        
        first_carousel = get_carousel.filter(id=1).first()
        if first_carousel is not None:
            json_data['firstcarousel'] = {
                "id" : first_carousel.id,
                "img" : first_carousel.img
            }
        else:
            json_data['firstcarousel'] = {
                "id" : "1",
                "img" : "#TODO Add default image"
            }

        last_carousel = get_carousel.filter(id=2).first()
        if last_carousel is not None:
            json_data['lastcarousel'] = {
                "id" : last_carousel.id,
                "img" : last_carousel.img
            }        
        else:
            json_data['lastcarousel'] = {
                "id" : "2",
                "img" : "#TODO Add default image"
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
                json_data['categoryspecialist']['categories'].append(data)

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
            status_code = status.HTTP_200_OK
        )

#---------Notifications Screen API --------------------
class PatientNotificationScreen(APIView):
    permission_classes = []
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
        query = PatientNotification.objects.all() #FIXME filter(patientid=patient)
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

#--------Doctors Details Display In Detail Screen API--------------------
class DoctorSlotDetails(APIView):
    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def get(self,request,format=None):
        """
            User is the current registered user.
            Doctor Id is the 'id' field of the doctor model whose details are to be displayed.
        """

        json_data = {
            "doctor" : {},
            "familymembers" : [],
            "dates" : [],
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
        }
        
        user = request.user

        doctorid = request.query_params.get('doctorid', None)
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
        }

        """
            Get all the family members of the requesting user.
            Appending the current user data details also
        """
        members = []
        user_mem = {
            "id" : user.id,
            "name" : user.name,
            "selected" : user.selected,
        }
        members.append(user_mem)

        for i in user.family_members:
            mem = {
                "id" : i['id'],
                "name" : i['name'],
                "selected" : i['selected'],
            }
            members.append(mem)    

        json_data['familymembers'] = members
        
        timings = DoctorTimings.objects.filter(doctor_id=doctor).first()
        dates_arr = []
        for j in timings.availability['dates_arr']:
            dt = dtt.strptime(j, "%m/%d/%Y").strftime(dmY)
            dates_arr.append(dt)
        json_data['dates'] = dates_arr

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

        mrngarr = timings.timeslots[timings.availability['dates_arr'][0]]['morning'] 
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

        noonarr = timings.timeslots[timings.availability['dates_arr'][0]]['afternoon'] 
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
        eveningarr = timings.timeslots[timings.availability['dates_arr'][0]]['evening'] 
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
        get_member = Patient.objects.filter(id=memberid).first()
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
            'gender' : [
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
                
            ],
            'experience': [
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

        user = request.user
        data = request.query_params
        query = data.get('search', "")
        search_type = data.get("search_type","first")
        specialist = data.get('specialist', None)
        exp = int(data.get('exp', 1))
        gender = data.get('gender','A')

        """
            Search for doctors in their names and their department wise
        """
        temp = []

        name_set = Doctor.objects.filter(name__icontains=query,is_blocked=False).all()
        name_serializer = DoctorSerializer(name_set,many=True,context={"request":request})
        for i in name_serializer.data:
            data = {
                "id" : i['id'],
                "doctor_id" : i['doctor_id'],
                "name" : i['name'],
                "experience" : i['experience'],
                "gender" : i['gender'],
                "deptid" : i['department_id']['id'],
                "deptname" : i['department_id']['name'],
            }
            temp.append(data)
        
        dept_set = Department.objects.filter(name__icontains=query).all()
        dept_serializer = DepartmentSerializer(dept_set,many=True,context={"request":request})
        for j in dept_serializer.data:
            queryset = Doctor.objects.filter(department_id__id=j['id'],is_blocked=False).all()
            queryset_serializer = DoctorSerializer(queryset,many=True,context={"request":request})
            for x in queryset_serializer.data:
                data = {
                    "id" : x['id'],
                    "doctor_id" : x['doctor_id'],
                    "name" : x['name'],
                    "experience" : x['experience'],
                    "gender" : x['gender'],
                    "deptid" : x['department_id']['id'],
                    "deptname" : x['department_id']['name'],
                }
                temp.append(data)

        category_set = CategorySpecialist.objects.filter(name__icontains=query).all()
        category_serializer = CategorySpecialistSerializer(category_set,many=True,context={"request":request})
        for k in category_serializer.data:
            queryset = Doctor.objects.filter(department_id__id=k['depts']['id'],is_blocked=False).all()
            queryset_serializer = DoctorSerializer(queryset,many=True,context={"request":request})
            for y in queryset_serializer.data:
                data = {
                    "id" : y['id'],
                    "doctor_id" : y['doctor_id'],
                    "name" : y['name'],
                    "experience" : y['experience'],
                    "gender" : y['gender'],
                    "deptid" : y['department_id']['id'],
                    "deptname" : y['department_id']['name'],
                }
                temp.append(data)

        final = []
        for a in temp:
            if a not in final:
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
                    for g in json_data['gender']:
                        if g['id'] == 'M':
                            g['selected'] = True
                        else:
                            g['selected'] = False
                elif gender=="F":
                    for f in initial:
                        if f['gender'] == 'F':
                            filter_1.append(f)
                    for g in json_data['gender']:
                        if g['id'] == 'F':
                            g['selected'] = True
                        else:
                            g['selected'] = False
                else:
                    filter_1 = initial
                    for g in json_data['gender']:
                        if g['id'] == 'A':
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
                print(exp)
                if exp == 2:
                    filter_1.sort(key=lambda e: e['experience'], reverse=False)
                    for e in json_data['experience']:
                        if e['id'] == 2:
                            e['selected'] = True
                        else:
                            e['selected'] = False
                elif exp == 3:
                    filter_1.sort(key=lambda e: e['experience'], reverse=True)
                    for e in json_data['experience']:
                        if e['id'] == 3:
                            e['selected'] = True
                        else:
                            e['selected'] = False
                else:
                    for e in json_data['experience']:
                        if e['id'] == 1:
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
#-------Data Filtering API --------
"""
class DoctorFilter(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self,request,format=None):
        
            # Filtering of doctors data.
            # GET method:
            #     query : [String(query),required] Previous query searched by the user.
            #     specialist : [String(id),optional] Specialist of the doctor will be filtered from the resulted doctors
            #     exp : [int(customid),optional] Experience of the doctor will be filtered from the resulted doctors
            #         1 - Relevance
            #         2 - Low to high
            #         3 - High to low
            #     gender : [String(customid),optional] Gender of the doctor will be filtered from the result of the search
            #         A - All 
            #         M - Male
            #         F - Female
       
        user = request.user
        data = request.query_params
        query = data.get('search', "")
        specialist = data.get('specialist', None)
        exp = data.get('experience', 1)
        gender = data.get('gender','A')
        
"""