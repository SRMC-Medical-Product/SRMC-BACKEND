'''Django imports'''
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate 
from django.db.models import Q
from django.conf import settings
from datetime import datetime as dtt , time , timedelta

'''imports'''
import uuid 
from urllib.parse import urlparse , parse_qs

from .models import *
from .serializer import *
from .authentication import  *

from mainapp.models import *
from mainapp.serializers import *
from mainapp.doctor_serializers import *
from mainapp.utils import *
from mainapp.auth import *

'''Response Import'''
from myproject.responsecode import display_response,exceptiontype,exceptionmsg

'''Rest Framework'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

'''encrypt'''
import hashlib 


'''Time Format Imports'''
from mainapp.utils import  dmY,Ymd,IMp,YmdHMS,dmYHMS,YmdTHMSf,YmdHMSf,HMS

from mainapp.serializers import *
from mainapp.doctor_serializers import *
from mainapp.models import *

#----------------------------Start : Admin Auth----------------------------
class AdminLogin(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self , request , format=None): 
        """
            Admin Login View:
            POST method:
                userid: [String,required] email/phone of the admin
                password: [String,required] password of the admin
        """
        data = self.request.data 
        userid = data.get('userid')
        password = data.get('password') 

        if userid is None or password is None:
            return display_response(
                msg='ERROR',
                err="Invalid data given",
                body = None,
                statuscode=status.HTTP_400_BAD_REQUEST,
            )
        encrypted_password = encrypt_superadmin_pass(password)
 
        get_user = SuperAdmin.objects.filter(Q(email=userid) | Q(phone= userid)).filter(password=encrypted_password).first()
        if get_user is None:
            return display_response(
                msg='ERROR',
                err="Invalid Credentials",
                body = None,
                statuscode=status.HTTP_400_BAD_REQUEST,
            )

        if get_user.active == False:
            return display_response(
                msg='ERROR',
                err="User does not has access to login",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST,
            )

        token=generate_token({"id":get_user.id})
        return display_response(
            msg='SUCCESS',
            err=None,
            body = {
                "superuser": True,
                "token": token,
            },
            statuscode = status.HTTP_200_OK,
        )
        
#----------------------------End : Admin Auth----------------------------

#----------------------------Start : Promotions and Homepage----------------------------
class CarouselView(APIView): 
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = [] 

    def get(self , request , format=None):
        ACTION = "Carousel GET" 
        snippet = Carousel.objects.all()
        serializer = CarouselSerializer(snippet, many=True , context={'request': request})
        return display_response( 
            msg = ACTION,
            err= None,
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )

    def post(self , request , format=None):
        ACTION = "Carousel POST" 
        data = self.request.data
        img = data.get('img')
        if img in [None , '']:
            return display_response(
            msg = ACTION,
            err= "Image not found",
            body = None,
            statuscode = status.HTTP_200_OK
        ) 
        count = Carousel.objects.count()
        if count < 2:

            try :
                Carousel.objects.create(img=img)

                return display_response(
                    msg = ACTION, 
                    err= None,
                    body = "Carousel Created Successfully",
                    statuscode = status.HTTP_200_OK
                )

            except Exception as e:
                excep = exceptiontype(e) 
                msg = exceptionmsg(e)
                return display_response(
                    msg = ACTION,
                    err= f"{excep} || {msg}",
                    body = None,
                    statuscode = status.HTTP_409_CONFLICT
                )
        else:
            return display_response(
                msg = ACTION,
                err= "Carousel limit (2) reached",
                body = None,
                statuscode = status.HTTP_200_OK
            )

    def delete(self , request , format=None):
        ACTION = "Carousel DELETE" 
        data = request.data 
        id = data.get('id') 
        if id in [None , '']:
            return display_response(
            msg = ACTION,
            err= "Id not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND 
        )   

        get_carousel = Carousel.objects.filter(id=id).first()  
        if get_carousel is None:
            return display_response(
            msg = ACTION,
            err= "Carousel not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND 
        )

        try :
            get_carousel.delete() 
            return display_response(
                msg = ACTION,
                err= None,
                body = "Carousel Deleted Successfully",
                statuscode = status.HTTP_200_OK
            )

        except Exception as e:
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )        

class PromotionalSliderView(APIView): 
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []  

    def get(self , request , format=None):
        ACTION = "PromotionalSlider GET" 
        snippet = PromotionalSlider.objects.all()
        serializer = PromotionalSliderSerializer(snippet, many=True , context={'request': request})
        return display_response( 
            msg = ACTION,
            err= None,
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )

    def post(self , request , format=None):
        ACTION = "PromotionalSlider POST" 
        data = self.request.data
        img = data.get('img')
        if img in [None , '']:
            return display_response(
            msg = ACTION,
            err= "Image not found",
            body = None,
            statuscode = status.HTTP_200_OK
        ) 
        try :
            PromotionalSlider.objects.create(img=img)
            return display_response(
                msg = ACTION, 
                err= None,
                body = "PromotionalSlider Created Successfully",
                statuscode = status.HTTP_200_OK
            )
        except Exception as e:
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )

    def delete(self , request , format=None):
        ACTION = "PromotionalSlider DELETE" 
        data = request.data 
        id = data.get('id') 
        if id in [None , '']:
            return display_response(
            msg = ACTION,
            err= "Id not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND 
        )   

        get_category_promotion = PromotionalSlider.objects.filter(id=id).first()  
        if get_category_promotion is None:
            return display_response(
            msg = ACTION,
            err= "PromotionalSlider not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND 
        )

        try :
            get_category_promotion.delete() 
            return display_response(
                msg = ACTION,
                err= None,
                body = "PromotionalSlider Deleted Successfully",
                statuscode = status.HTTP_200_OK
            )

        except Exception as e:
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )        

class CategoryPromotionView(APIView): 
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = [] 

    def get(self , request , format=None): 
        ACTION = "CategoryPromotion GET"
        snippet = CategoryPromotion.objects.all()
        serializer = CategoryPromotionSerializer(snippet, many=True , context={'request': request}) 
        return display_response(
            msg = ACTION,
            err= None,
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )
 
    def post(self , request , format=None):
        ACTION = "CategoryPromotion POST"
        data = self.request.data
        title = data.get('title')
        category = data.get('category')

        if title in [None , ''] or category in [None , '']: 
            return display_response(
            msg = ACTION,
            err= "Title or Category not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        ) 

        get_category = CategorySpecialist.objects.filter(id=category).first() 
        if get_category is None: 
            return display_response(
            msg = ACTION,
            err= "Category object does not exists",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        ) 

        try :
            CategoryPromotion.objects.create(
                title=title, 
                category=get_category
            )
            return display_response(
                msg = ACTION,
                err= None,
                body = "CategoryPromotion Created Successfully",
                statuscode = status.HTTP_201_CREATED
            )

        except Exception as e:
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )

    def delete(self , request , format=None):
        ACTION = "CategoryPromotion DELETE"
        data = request.data
        id = data.get('id')
        if id in [None , '']:
            return display_response(
            msg = ACTION,
            err= "Id not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        get_category_promotion = CategoryPromotion.objects.filter(id=id).first()
        if get_category_promotion is None:
            return display_response(
            msg = ACTION,
            err= "CategoryPromotion not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        try :
            get_category_promotion.delete()
            return display_response(
                msg = ACTION,
                err= None,
                body = "CategoryPromotion Deleted Successfully",
                statuscode = status.HTTP_200_OK
            )

        except Exception as e: 
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )
#----------------------------End : Promotions and Homepage----------------------------

#---Get all Admin Available----
class AdminData(APIView):
    authentication_classes = [SuperAdminAuthentication] 
    permission_classes = [] 
    
    def get(self , request, format=None):
        ACTION = "AdminData GET"
        snippet = SuperAdmin.objects.all()

        if snippet is None:
            return display_response(
            msg = ACTION,
            err= "No data found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = SuperAdminSerializer(snippet,many=True,context={'request' :request}) .data
        json_data = serializer
        
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Get particular Admin User----
class AdminUserGet(APIView): 
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []
    
    def get(self, request,format=None):
        ACTION = "AdminModify GET"
        user = request.user
        serializer = SuperAdminSerializer(user,context={'request' :request}).data
        return display_response(
            msg = ACTION,
            err= None,
            body = serializer,
            statuscode = status.HTTP_200_OK
        )

#---Admin Data Modify----
class AdminUserModify(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def put(self,request,format=None):
        ACTION = "AdminModify PUT"
        user = request.user
        data = request.data
        username = data.get('name')
        email = data.get('email')    
        phone = data.get('phone') 


        if email not in [None , ""]:
            email_check = SuperAdmin.objects.filter(email=email).first()
            if email_check is not None:
                return display_response(
                    msg = ACTION,
                    err= "Email already exists",
                    body = None,
                    statuscode = status.HTTP_409_CONFLICT
                )

        if phone not in [None , ""]:
            phone_check = SuperAdmin.objects.filter(phone=phone).first()
            if phone_check is not None:
                return display_response(
                    msg = ACTION,
                    err= "Phone number already exists",
                    body = None,
                    statuscode = status.HTTP_409_CONFLICT
                )

        if email not in [None , ""]:
            user.email = email

        if phone not in [None , ""]:
            user.phone = phone

        if username not in [None , ""]:
            user.name = username
            
        user.save()    
        
        return display_response(
            msg = ACTION,
            err= None,
            body = "User Modified Successfully",
            statuscode = status.HTTP_200_OK
        ) 

#----Change Super Admin Password--------------------------------
class AdminUserPasswordModify(APIView):

    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def put(self,request,format=None):
        ACTION = "AdminPasswordModify PUT"
        user = request.user
        data = request.data
        oldpassword = data.get('oldpassword',None)
        newpassword = data.get('newpassword',None)

        '''Check for None Values'''
        if oldpassword in [None,""] or newpassword in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Password data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )    

        encrypted_oldpass = encrypt_superadmin_pass(oldpassword)
        if encrypted_oldpass != user.password:
            return display_response(
                msg = ACTION,
                err= "Old Password is incorrect",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        encrypted_newpass = encrypt_superadmin_pass(newpassword)
        user.password = encrypted_newpass
        user.save()

        return display_response(
            msg = ACTION,
            err= None,
            body = "User Modified Successfully",
            statuscode = status.HTTP_200_OK
        )    
 
#----Departments -----------
class DepartmentsView(APIView):

    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []
    
    '''Get All Departments'''
    def get(self , request, format=None):
        ACTION = "Departments GET"
        snippet = Department.objects.all()
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

    '''Create New Departments'''
    def post(self, request, format=None):
        """
            To create a department,first check the vaid fields and get the 
            json_data format of counter and append it to the counter(JSonfield)
            --------------------
            POST method:
                name : [String,required] name of the department
                img : [String,required] image of the department
                head : [String,required] head of the department
                counter : [JSON,required] counter details
                ------------------------------------------
                counter : [
                    {
                        "counter": "counter",
                        "floor": "floor",
                    },
                    {
                        "counter": "counter",
                        "floor": "floor",
                    },
                ]
        """
        data = request.data
        name = data.get('name',None) 
        img = data.get('img',None)
        head = data.get('head',None) 
        counter = data.get('counter',None)

        '''Check for None Values'''
        if name in [None,""] or img in [None , ""] or head in [None ,""] or counter in [None , ""]:
            return display_response(
            msg = "Error",
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        counter_list = []
        for i in counter:
            id = str(uuid.uuid4().hex[0:4]) + str(len(counter_list)+1)
            data = {
                "id":id,
                "counter":i["counter"],
                "floor":i["floor"],
                "created_at": str(dtt.now(IST_TIMEZONE)),
            }
            counter_list.append(data)
        """Save not null values"""
        try:
            department = Department.objects.create(
                name = name,
                img = img,
                head = head,
                counter = counter_list,
            )
            return display_response(
                msg = "Success",
                err= None,
                body = "Department Created Successfully",
                statuscode = status.HTTP_201_CREATED
            )
        except Exception as e:
            print(e)
            return display_response(
                msg = "Error",
                err= "Department Creation Failed",
                body = None,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

    ''' Modify Departments'''
    def put(self,request,format=None):
        ACTION = "Departments PUT"
        data = request.data
        id = data.get('id') 
        name = data.get('name') 
        img = data.get('img')
        head = data.get('head') 
        enable = data.get('enable')

        '''Check for None Values'''
        if id in [None , ""] :
            return display_response(
            msg = ACTION,
            err= "ID was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        
        '''Checking if ID object exists'''
        get_department = Department.objects.filter(id=id).first() 
        if get_department is None:
            return display_response(
            msg = ACTION,
            err= "Department Object was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        '''Checking if Name object exists''' 
        if name not in [None , ""]:
            get_department.name = name 
            get_department.save()

        '''Checking if img object exists''' 
        if img not in [None , ""]:
            get_department.img = img 
            get_department.save()

        '''Checking if head object exists''' 
        if head not in [None , ""]:
            get_department.head = head 
            get_department.save()
        
        '''Checking if enable object exists''' 
        if enable not in [None , ""] and enable in [True,False]:
            get_department.enable = enable 
            get_department.save()
        
        return display_response(
            msg = ACTION,
            err= None,
            body = "Department Modified Successfully",
            statuscode = status.HTTP_200_OK 
        )

#-----Category Specialization-----
class CategorySpecialistView(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    '''Get All CategorySpecialist''' 
    def get(self , request , format =None):
        ACTION = "CategorySpecialist GET"
        snippet = CategorySpecialist.objects.all()
        if snippet is None:
            return display_response(
            msg = ACTION,
            err= "No data found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = CategorySpecialistSerializer(snippet,many=True,context={'request' :request})
        return display_response(
            msg = ACTION,
            err= None,
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )

    '''Create New CategorySpecialist'''
    def post(self, request, format=None):
        ACTION = "CategorySpecialist POST"
        data = request.data
        name = data.get('name')
        img = data.get('img') 

        '''Check for None Values'''
        if name in [None,""] or img in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        ) 

        print(name , img)
        try:
            CategorySpecialist.objects.create(
                name = name,
                img = img,
            )
            '''Adding the Department to the CategorySpecialist'''  
            return display_response(
                msg = ACTION,
                err= None,
                body = "CategorySpecialist Created Successfully",
                statuscode = status.HTTP_201_CREATED
            )
        except Exception as e:
            excep = exceptiontype(e)
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )

    def put(self , request , format=None):

        ACTION = "CategorySpecialist PUT"
        data = request.data
        id = data.get('id')
        name = data.get('name')
        img = data.get('img')

        '''Check for None Values'''
        if id in [None , ""] or name in [None , ""] or img in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        '''Checking if ID object exists'''
        get_category_specialist = CategorySpecialist.objects.filter(id=id).first()
        if get_category_specialist is None:
            return display_response(
            msg = ACTION,
            err= "CategorySpecialist Object was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        '''Checking if Name exists'''
        if name not in [None , ""]:
            get_category_specialist.name = name 
            get_category_specialist.save()
        
        '''Checking if image exists'''        
        if img not in [None , ""]:
            get_category_specialist.img = img 
            get_category_specialist.save()

        return display_response(
            msg = ACTION,
            err= None,
            body = "CategorySpecialist Modified Successfully",
            statuscode = status.HTTP_200_OK 
        )

#---Doctors Available---------                  
class DoctorGet(APIView):
    authentication_classes = [SuperAdminAuthentication] 
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
        search = request.query_params.get("search",None)
        isblocked = request.query_params.get("isblocked",False)

        snippet = Doctor.objects.all() 

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
    authentication_classes = [SuperAdminAuthentication] 
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
    authentication_classes = [SuperAdminAuthentication] 
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
        search = request.query_params.get("search",None)
        primaryuser = request.query_params.get("primary",False)
        
        
        snippet = Patient.objects.all()
        
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
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            This view displays the particular doctor details
            ----------------------------------------------------------------
            GET method:
                patentid : [String,required] patient id
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


'''Patient Users get'''
class PatientAppUsers(APIView): 
    authentication_classes = [SuperAdminAuthentication] 
    permission_classes = []

    def get(self , request , format=None):
        ACTION = "Users GET"
        snippet = User.objects.all() 
        serializer = UserSerializer(snippet,many=True,context={'request' :request}).data
        return display_response(
            msg = ACTION,
            err= None, 
            body = serializer,
            statuscode = status.HTTP_200_OK
        )

#---All HelpDeskTeam----
class HelpDeskTeam(APIView):
    authentication_classes = [SuperAdminAuthentication] 
    permission_classes = []

    def get(self , request , format=None):
        ACTION = "HelpDeskTeam GET"
        json_data = {
            "isempty" : True,
            "team" : [],
        }
        snippet = HelpDeskUser.objects.all() 
        serializer = HelpDeskUserSerializer(snippet,many=True,context={'request' :request}).data
        for i in serializer:
            data = {
                "id" : i['id'],
                "name" : i['name'],
                "email" : i['email'],
                "mobile" : i['mobile'],
                "is_blocked" : i['is_blocked'],
            }
            json_data['team'].append(data)
        
        if len(json_data['team']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = ACTION,
            err= None, 
            body = json_data,
            statuscode = status.HTTP_200_OK
        ) 

    def post (self , request , format = None): 
        """
            This view creates a new HelpDeskUser
            ----------------------------------------------------------------
            POST method:
                name : [String,required] name of the user
                email : [String,required] email of the user
                mobile : [String,required] mobile of the user
                pin : [String,required] pin of the user
                specialisation : [List,required] specialisation of the user.List of ids
                    
        """
        ACTION = "HelpDeskTeam POST"
        data = request.data
        name = data.get('name',None)
        email = data.get('email',None) 
        mobile = data.get('mobile',None)
        pin = data.get('pin',None)
        specialisation = data.get('specialisation',[])

        if name in [None , ""] or email in [None , ""] or mobile in [None , ""] or pin in [None , ""] or len(specialisation) == 0 :
            return display_response(
                msg = ACTION,
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            ) 

        check_email = HelpDeskUser.objects.filter(email=email).first()
        if check_email is not None:
            return display_response(
                msg = ACTION,
                err= "Email already exists",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        check_mobile = HelpDeskUser.objects.filter(mobile=mobile).first()
        if check_mobile is not None:
            return display_response(
                msg = ACTION,
                err= "Mobile number already exists",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        ''' checking if specialisation id exists'''
        for i in range(len(specialisation)):
            specialisation_instance = Department.objects.filter(id=specialisation[i]).first() 
            if specialisation_instance is None: 
                return display_response(
                    msg = ACTION,
                    err= "Department id not found",
                    body = None,
                    statuscode = status.HTTP_404_NOT_FOUND
                )
    

        '''create support user object '''
        try: 
            
            '''encrypt pin and save'''
            encrypted_pin = encrypt_helpdesk_pin(pin)

            support_user = HelpDeskUser.objects.create(  
                name = name,
                email = email,
                mobile = mobile,
                pin = encrypted_pin,
            )

            '''create many to many relation''' 
            for k in range(len(specialisation)):
                specialisation_instance = Department.objects.filter(id=specialisation[k]).first() 
                if specialisation_instance is not None: 
                    support_user.specialisation.add(specialisation_instance)
                
            return display_response( 
                msg = ACTION,
                err= None,
                body = "Successfully Support User created", 
                statuscode = status.HTTP_201_CREATED
            )
        except Exception as e:
            excep = exceptiontype(e) 
            msg = exceptionmsg(e)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
            )
     
#---UnBlock/Block help Desk User----
class AccessHelpDeskUser(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def put(self , request , format=None):
        """
            Block the help desk user here.
            PUT method:
                id = [String,required] id of the help desk user
                block = [Boolean,required] True or False of the help desk user 
        """
        data = request.data
        id = data.get('id',None)
        block = data.get('block',None)
        if id in [None , ""] or block in [None , ""]:
            return display_response(
                msg = "ERROR",
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        helpdesk_user = HelpDeskUser.objects.filter(id=id).first()
        if helpdesk_user is None:
            return display_response(
                msg = "ERROR",
                err= "HelpDeskUser not found",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        if block in [True,'True']:
            if helpdesk_user.is_blocked == True:
                return display_response(
                    msg = "ERROR",
                    err= "HelpDeskUser is already blocked",
                    body = None,
                    statuscode = status.HTTP_404_NOT_FOUND
                )
            else:
                helpdesk_user.is_blocked = True
                helpdesk_user.save()
                return display_response(
                    msg = "SUCCESS",
                    err= None,
                    body = "Successfully blocked",
                    statuscode = status.HTTP_200_OK
                )

        if block in [False,'False']:
            if helpdesk_user.is_blocked == False:
                return display_response(
                    msg = "ERROR",
                    err= "HelpDeskUser is already unblocked",
                    body = None,
                    statuscode = status.HTTP_404_NOT_FOUND
                )
            else:
                helpdesk_user.is_blocked = False
                helpdesk_user.save()
                return display_response(
                    msg = "SUCCESS",
                    err= None,
                    body = "Successfully unblocked",
                    statuscode = status.HTTP_200_OK
                )

        return display_response(
            msg = "ERROR",
            err= "Block field found some else value instead of True/False",
            body = None,
            statuscode = status.HTTP_200_OK
        )

#---UnBlock/Block Doctor User----
class AccessDoctorUser(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def put(self , request , format=None):
        """
            Block the help desk user here.
            PUT method:
                id = [String,required] id of the doctor user
                block = [Boolean,required] True or False of the doctor user 
        """
        data = request.data
        id = data.get('id',None)
        block = data.get('block',None)
        if id in [None , ""] or block in [None , ""]:
            return display_response(
                msg = "ERROR",
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        doctor_user = Doctor.objects.filter(id=id).first()
        if doctor_user is None:
            return display_response(
                msg = "ERROR",
                err= "HelpDeskUser not found",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        if block in [True,'True']:
            if doctor_user.is_blocked == True:
                return display_response(
                    msg = "ERROR",
                    err= "Doctor is already blocked",
                    body = None,
                    statuscode = status.HTTP_404_NOT_FOUND
                )
            else:
                doctor_user.is_blocked = True
                doctor_user.save()
                return display_response(
                    msg = "SUCCESS",
                    err= None,
                    body = "Successfully blocked",
                    statuscode = status.HTTP_200_OK
                )

        if block in [False,'False']:
            if doctor_user.is_blocked == False:
                return display_response(
                    msg = "ERROR",
                    err= "HelpDeskUser is already unblocked",
                    body = None,
                    statuscode = status.HTTP_404_NOT_FOUND
                )
            else:
                doctor_user.is_blocked = False
                doctor_user.save()
                return display_response(
                    msg = "SUCCESS",
                    err= None,
                    body = "Successfully unblocked",
                    statuscode = status.HTTP_200_OK
                )

        return display_response(
            msg = "ERROR",
            err= "Block field found some else value instead of True/False",
            body = None,
            statuscode = status.HTTP_200_OK
        )

#---Help Desk USer Details --------------------------------
class HelpDeskUserDetails(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get the help desk user details here.
            GET method:
                id = [String,required] id of the help desk user
        """
        data = request.query_params
        id = data.get('id',None)
        if id in [None , ""]:
            return display_response(
                msg = "ERROR",
                err= "Data was found None",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        helpdesk_user = HelpDeskUser.objects.filter(id=id).first()
        if helpdesk_user is None:
            return display_response(
                msg = "ERROR",
                err= "HelpDeskUser not found",
                body = None,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        serializer = HelpDeskUserSerializer(helpdesk_user,context={'request' :request}).data

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = serializer,
            statuscode = status.HTTP_200_OK
        )

#---Get all Appointments --------------------------------
class GetAllAppointments(APIView):
    authentication_classes = [SuperAdminAuthentication]
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
        if aset in [1,'1']:
            appointments = Appointment.objects.filter(date=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False).order_by('-time')
            json_data['livetoday'] = True
            json_data['pending'] = False
            json_data['upcoming'] = False
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [2,'2']:
            appointments = Appointment.objects.filter(date__lt=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False).order_by('-date')
            json_data['livetoday'] = False
            json_data['pending'] = True
            json_data['upcoming'] = False
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [3,'3']:
            appointments = Appointment.objects.filter(date__gt=dtt.now(IST_TIMEZONE).strftime(Ymd),closed=False).order_by('date')
            json_data['livetoday'] = False
            json_data['pending'] = False
            json_data['upcoming'] = True
            json_data['history'] = False
            json_data['all'] = False
        elif aset in [4,'4']:
            appointments = Appointment.objects.filter(closed=True).order_by('-date')
            json_data['livetoday'] = False
            json_data['pending'] = False
            json_data['upcoming'] = False
            json_data['history'] = True
            json_data['all'] = False
        else:
            appointments = Appointment.objects.all().order_by('-date')
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

#---Department and its Doctors --------------------------------
class DepartmentDoctors(APIView):
    authentication_classes = [SuperAdminAuthentication]
    permission_classes = []

    def get(self , request , format=None):
        """
            Get all the departments and their doctors here.
            ---------------------
            GET method:
                deptid : [String,required] id of the department
                search : [String,optional] search the doctors
        """
        json_data ={
            "isempty" : True,
            "deptid" : "",
            "doctors" : [],
        }
        deptid = request.query_params.get("deptid",None)
        search = request.query_params.get("search",None)

        if deptid in [None , ""]:
            return display_response(
                msg = "FAILED",
                err= "Department id is required",
                body = json_data,
                statuscode = status.HTTP_400_BAD_REQUEST
            )

        dept = Department.objects.filter(id=deptid).first()
        if dept in [None , ""]:
            return display_response(
                msg = "FAILED",
                err= "Department not found",
                body = json_data,
                statuscode = status.HTTP_404_NOT_FOUND
            )

        doctors = Doctor.objects.filter(department_id=dept).order_by('name')
        
        if search not in [None , ""]:
            doctors = doctors.filter(Q(name__icontains=search))
        
        serializer = DoctorSerializer(doctors,many=True,context={'request' :request}).data

        for i in serializer:
            data = {
                "id" : i['id'],
                "name" : i['name'],
                "doctor_id" : i['doctor_id'],
                "phone" : i['phone'],
                "email" : i['email'],
                "profile_img" : i['profile_img'],
                "age" : i['age'],
                "gender" : i['gender'],
                "qualification" : i['qualification'],
            }
            json_data['doctors'].append(data)

        json_data['deptid'] = deptid

        if len(json_data['doctors']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

#---Tickets --------------------------------
class AllPatientTickets(models.Model):
    authentication_classes = [SuperAdminAuthentication]
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
            "closed" : False,
        }

        params = request.query_params
        search = params.get("search",None)
        closed = params.get("closed",False)
        
        query = PatientTickets.objects.all().order_by('-created_at')

        if closed in [True ,'True']:
            query = query.filter(closed=True)
            json_data['closed'] = True
        else:
            query = query.filter(closed=False)
            json_data['closed'] = False
        
        if search not in [None , ""]:
            query = query.filter(Q(user_id__name__icontains=search))

        serializer = PatientTicketsSerializer(query,many=True,context={'request' :request}).data
        json_data['tickets'] = serializer

        if len(json_data['tickets']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

class AllDoctorTickets(models.Model):
    authentication_classes = [SuperAdminAuthentication]
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
            "closed" : False,
        }

        params = request.query_params
        search = params.get("search",None)
        closed = params.get("closed",False)
        
        query = DoctorTickets.objects.all().order_by('-created_at')

        if closed in [True ,'True']:
            query = query.filter(closed=True)
            json_data['closed'] = True
        else:
            query = query.filter(closed=False)
            json_data['closed'] = False
        
        if search not in [None , ""]:
            query = query.filter(Q(doctor_id__name__icontains=search))

        serializer = DoctorTicketsSerializer(query,many=True,context={'request' :request}).data
        json_data['tickets'] = serializer

        if len(json_data['tickets']) > 0:
            json_data['isempty'] = False

        return display_response(
            msg = "SUCCESS",
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )


















