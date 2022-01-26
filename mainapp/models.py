from distutils.ccompiler import gen_lib_options
from django.db import models

# Create your models here.
class User(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    mobile=models.CharField(max_length=15,unique=True)
    aadhar_number=models.CharField(max_length=12,unique=True,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    family_members=models.JSONField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

class UserStatistics(models.Model):

    year=models.PositiveIntegerField()
    count=models.BigIntegerField(default=0,editable=False)

    def __str__(self):
        return f"{self.year}"

class UserOtp(models.Model):

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)
    code=models.CharField(max_length=10)
    expiry_time=models.DateTimeField()

    def __str__(self):
        return self.otp+self.code





class Department(models.Model):
    
    id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
    name=models.CharField(max_length=100)
    head=models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.id

class Doctor(models.Model):

    id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
    doctor_id=models.CharField(max_length=256,unique=True)
    name=models.CharField(max_length=256)
    pin=models.CharField(max_length=5)
    age=models.PositiveIntegerField()
    gender=models.CharField(max_length=1)
    dob=models.DateField()
    expirence=models.PositiveIntegerField()
    qualification=models.TextField()
    specialisation=models.TextField()
    languages_known=models.TextField()
    modified_at=models.DateTimeField(editable=False)
    
    department_id=models.ForeignKey(Department,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.id


class DoctorTimings(models.Model):

    doctor_id=models.ForeignKey(Doctor,on_delete=models.CASCADE)
    availability=models.JSONField(null=True,blank=True)
    timeslots=models.JSONField(default=dict,blank=True)
    modified_at=models.DateTimeField(null=True,blank=True)
    start_time=models.TimeField()
    end_time=models.TimeField()
    average_appoinment_duration=models.PositiveIntegerField()

    def __str__(self):
        
        return str(self.id)