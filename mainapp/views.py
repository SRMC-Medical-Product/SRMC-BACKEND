from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


from .models import *
from .auth import *
from .serializers import *
from .tasks import test_func

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
        test_func.delay()
        return Response({
                    "MSG":"SUCCESS",
                    "ERR":None,
                    "BODY":serializer.data
                        },status=status.HTTP_200_OK)
                        

class AddFamilyMember(APIView):

    """
        API View to add family member to a particular user
        With the given data a new user instance is created.

        Allowed Methods:
            -POST
        
        Request data:
            name:   [String,required] name of the patient
            number  [String,required] mobile number of the patient
            email:  [String] email id of the patient
            aadhar: [String] aadhar number of the patient
        
        Authentication:
            -Required
            -UserAuthentication
    
    """

    authentication_classes=[UserAuthentication]
    permission_classes=[]


    def post(self,request,format=None):

        data=request.data

        name=data.get("name",None)     #required
        number=data.get("number",None) #required

        email=data.get("email",None)
        aadhar=data.get("aadhar",None)

        #validating the user data
        if name in [None,""] or number in [None,""]:

            return Response({
                    "MSG":"FAILED",
                    "ERR":"Please provide valid name and number",
                    "BODY":None
                         },status=status.HTTP_400_BAD_REQUEST)
        
        family_member=User.objects.filter(mobile=number)

        if family_member.exists():
            family_member=family_member[0]
        else:
            
            family_member=User.objects.get_or_create(name=name,mobile=number,email=email,aadhar_number=aadhar)[0]



        family_serialized_data=UserSerializer(family_member).data

        user=request.user
        if user==family_member:

            return Response({
                        "MSG":"FAILED",
                        "ERR":"You can't add yourself again",
                        "BODY":None
                            },status=status.HTTP_400_BAD_REQUEST)

        if user.family_members==None:
            user.family_members=[family_serialized_data]
        else:
            user.family_members.append(family_serialized_data)
        
        user.save()

        return Response({
                "MSG":"SUCCESS",
                "ERR":None,
                "BODY":"Family member added successfully"
                    },status=status.HTTP_200_OK)
