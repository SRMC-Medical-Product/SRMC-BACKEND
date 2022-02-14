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