'''Django imports'''
from django.contrib.auth.models import User
from django.contrib.auth import authenticate 
from django.db.models import Q
from django.conf import settings
from datetime import datetime as dtt , time , timedelta

'''imports'''
import uuid 
import math 
from urllib.parse import urlparse , parse_qs

'''Authentication Permission'''
from .authentication import AdminAuthentication

'''Model Import'''
from .models import *
from mainapp.models import *
from .authentication import  *

'''Serializer Import'''
from .serializer import *
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

#----------------------------Start : Admin Auth----------------------------
'''Admin Registration'''
class AdminRegister(APIView):
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission]
    
   #TODO : by aravind S (Backend developer)
    # def post(self , request , format=None):
    #     ACTION = "AdminRegister"
    #     is_superuser = False
    #     data = self.request.data
    #     username = data.get('username')
    #     email = data.get('email')
    #     password = data.get('password')
    #     is_superstaff=data.get("is_superstaff")
        
    #     print(data)
    #     if is_superstaff == True:
    #         is_superstaff = True
        
    #     if username is None or email is None or password is None:
    #         return display_response(
    #         msg = ACTION,
    #         err= "Values found null",
    #         body = None,
    #         statuscode = status.HTTP_200_OK
    #     )  

    #     print("60")
    #     # todo ERROR : keyword error username
    #     user=User.objects.filter(username=username)
    #     print(user)
    #     if user.exists():
    #          return display_response(
    #         msg = ACTION,
    #         err= "User already exists",
    #         body = None,
    #         statuscode = status.HTTP_200_OK
    #     )  
    #     if len(password) < 8:
    #         return display_response(
    #         msg = ACTION,
    #         err= "Password must be atleast 8 characters long",
    #         body = None,
    #         statuscode = status.HTTP_200_OK
    #     ) 

    #     user=User.objects.create(username=username,email=email,is_staff=True,is_superuser=is_superuser)
    #     user.set_password(password)
    #     user.save()
    #     return display_response(
    #         msg = ACTION,
    #         err= None,
    #         body = "User Created Successfully",
    #         statuscode = status.HTTP_200_OK
    #     ) 
    
'''Admin Login'''
#TODO : by aravind S (Backend developer)
class AdminLogin(APIView):

    authentication_classes=[]
    permission_classes=[]

    # def post(self , request , format=None): 
    #     ACTION = "Admin Login"
    #     data = self.request.data 
    #     username = data.get('username')
    #     password = data.get('password') 
    #     user = authenticate(username=username, password=password) 
    #     print(user)
    #     if user is not None:
    #         token = Token.objects.get_or_create(user=user) 
    #         if(user.is_superuser):
    #             return Response({"RESPONSE":{"token":token[0].key,"superuser":True}},status=status.HTTP_200_OK)
    #         return Response({"RESPONSE":{"token":token[0].key}},status=status.HTTP_200_OK)
    #     return Response({"RESPONSE":"Invalid credentials given"},status=status.HTTP_400_BAD_REQUEST)
        
#----------------------------End : Admin Auth----------------------------

#----------------------------Start : Promotions and Homepage----------------------------
class CarouselView(APIView): 
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission] 

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
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission] 

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
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission] 

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
        title = data.get('img')
        category = data.get('category')

        if title in [None , ''] or category in [None , '']: 
            return display_response(
            msg = ACTION,
            err= "Title or Category not found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        ) 

        get_category = CategorySpecialist.objects.filter(category=category).first() 
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

'''Admin Data Get'''
'''Bearer Token Required'''
class AdminData(APIView):
    serializer_class = AdminDataSerializer
    authentication_classes = [AdminAuthentication] #disables authentication
    permission_classes = [SuperAdminPermission] #disables permission
    
    def get(self , request, format=None):
        ACTION = "AdminData GET"
        snippet = User.objects.all()
        print(snippet)
        if snippet is None:
            return display_response(
            msg = ACTION,
            err= "No data found",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = AdminDataSerializer(snippet,many=True,context={'request' :request}) 
        json_data = []
        for i in serializer.data:
            json_data.append({
                "id":i["id"],
                "username":i["username"],
                "email":i["email"],
                "is_superuser":i["is_superuser"],
            })
        return display_response(
            msg = ACTION,
            err= None,
            body = json_data,
            statuscode = status.HTTP_200_OK
        )

'''Admin Each User Data Get'''
'''Bearer Token Required'''
class AdminUserGet(APIView):
    serializer_class = AdminDataSerializer 
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission]
    
    def get(self, request,format=None):
        ACTION = "AdminModify GET"
        data = request.user
        print(data)
        snippet = User.objects.filter(username=data)
        print(snippet) 
        if snippet is None:
            return display_response(
            msg = ACTION,
            err= "AdminData objects are None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )
        serializer = AdminDataSerializer(snippet,many=True,context={'request' :request})
        return display_response(
            msg = ACTION,
            err= None,
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )

'''Admin Modify Data'''
'''Bearer Token Required'''
class AdminUserModify(APIView):
    serializer_class = AdminDataSerializer 
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission]

    def put(self,request,format=None):
        ACTION = "AdminModify PUT"
        data = request.data
        id = data.get('id')
        username = data.get('username')
        email = data.get('email')    

        '''Check for None Values'''
        if id in [None,""]:
            return display_response(
            msg = ACTION,
            err= "ID was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )  

        """Get particular User"""
        get_user = User.objects.filter(id=id).first() 
        if get_user is None:
            return display_response(
            msg = ACTION,
            err= "User was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )  

        checkUsername = User.objects.filter(username=username)
        for i in checkUsername :
            if i.username == username:
                return display_response(
            msg = ACTION,
            err= "User with username already exists.Give a different username",
            body = None,
            statuscode = status.HTTP_400_BAD_REQUEST
        )   
        checkEmail = User.objects.filter(email=email)
        for i in checkEmail:
            if i.email == email:
                return display_response(
            msg = ACTION,
            err= "User with email already exists.Give a different username",
            body = None,
            statuscode = status.HTTP_400_BAD_REQUEST
        )    
        """Save not null values"""
        
        if username not in [None , ""]:
            get_user.username = username
            get_user.save()
       
        if email not in [None , ""]:
            get_user.email = email
            get_user.save()
        return display_response(
            msg = ACTION,
            err= None,
            body = "User Modified Successfully",
            statuscode = status.HTTP_200_OK
        ) 

'''Admin User Password'''
'''Bearer Token Required'''
# TODO : Add Password Encryption
class AdminUserPasswordModify(APIView):

    serializer_class = AdminDataSerializer 
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission]

    def put(self,request,format=None):
        ACTION = "AdminPasswordModify PUT"
        data = request.data
        id = data.get('id')
        password = data.get('password')  

        '''Check for None Values'''
        if id in [None,""]:
            return display_response(
            msg = ACTION,
            err= "ID was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )    
        """Get particular User"""
        get_user = User.objects.filter(id=id).first() 
        if get_user is None:
            return display_response(
            msg = ACTION,
            err= "User was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )    
        """Save not null values"""

        if password not in [None , ""]:
            get_user.set_password(password)
            get_user.save()
        return display_response(
            msg = ACTION,
            err= None,
            body = "User Modified Successfully",
            statuscode = status.HTTP_200_OK
        )    
 
'''Department Get'''
'''Bearer Token Required'''

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

    '''Create New Departments'''
    def post(self, request, format=None):
        ACTION = "Departments POST"
        data = request.data
        name = data.get('name') 
        img = data.get('img')
        head = data.get('head') 
        catspl_id = data.get('catspl_id')


        '''Check for None Values'''
        if name in [None,""] or img in [None , ""] or head in [None ,""] or catspl_id in [None , ""]:
            return display_response(
            msg = ACTION,
            err= "Data was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        '''Checking if Department Object exists'''
        get_category_specialist = CategorySpecialist.objects.filter(id=catspl_id).first()
        if get_category_specialist is None:
            return display_response(
            msg = ACTION,
            err= "Department Object was found None",
            body = None,
            statuscode = status.HTTP_404_NOT_FOUND
        )

        ''' Create a UID'''
        while True:
            uid = uuid.uuid4()
            '''Checking if the values uid is not available'''
            check_uid = Department.objects.filter(id=uid).first()
            if check_uid is None:
                break  
        '''Getting the uid Instance of Deparments'''
        try:
            new_department = Department.objects.create(
                id = uid,
                name = name,
                img = img,
                head = head,
                )
            get_category_specialist.depts.add(new_department)
            return display_response(
                msg = ACTION,
                err= None,
                body = "Department Created Successfully",
                statuscode = status.HTTP_201_CREATED
            )
        except Exception as exception :
            excep = exceptiontype(exception)
            msg = exceptionmsg(exception)
            return display_response(
                msg = ACTION,
                err= f"{excep} || {msg}",
                body = None,
                statuscode = status.HTTP_409_CONFLICT
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

class CategorySpecialistView(APIView):
    # authentication_classes = [AdminAuthentication]
    # permission_classes = [SuperAdminPermission]

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
 
        while True:
            uid = uuid.uuid4()
            '''Checking if the values uid is not available'''
            check_uid = CategorySpecialist.objects.filter(id=uid).first()
            if check_uid is None:
                break 
        print(name , img)
        try:
            CategorySpecialist.objects.create(
                id = uid,
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

''' custom json format to retrive in dashboard '''
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

''' custom json format to retrive doctor data in dashboard '''
class DoctorGet(APIView):
    authentication_classes = [AdminAuthentication] 
    permission_classes = [SuperAdminPermission]

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
    authentication_classes = [AdminAuthentication] 
    permission_classes = [SuperAdminPermission]

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

''' Patients get'''
class PatientGet(APIView):
    authentication_classes = [AdminAuthentication] 
    permission_classes = [SuperAdminPermission]     
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
    authentication_classes = [AdminAuthentication]
    permission_classes = [SuperAdminPermission] 
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

''' Users get'''
class UsersGet(APIView): 
    authentication_classes = [AdminAuthentication] 
    permission_classes = [SuperAdminPermission]
    def get(self , request , format=None):
        ACTION = "Users GET"
        snippet = User.objects.all() 
        serializer = UserSerializer(snippet,many=True,context={'request' :request})
        return display_response(
            msg = ACTION,
            err= None, 
            body = serializer.data,
            statuscode = status.HTTP_200_OK
        )


       
