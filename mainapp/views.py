from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


from .models import *
from .auth import *
from .serializers import *

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
        user_instance=User.objects.get_or_create(mobile=number)[0]
        
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

class UserProfile(APIView):

    authentication_classes=[UserAuthentication]
    permission_classes=[]

    def get(self,request,format=None):

        serializer=UserSerializer(request.user)

        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":serializer.data
                        },status=status.HTTP_200_OK)
                        