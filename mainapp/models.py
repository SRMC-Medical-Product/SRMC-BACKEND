from django.db import models


'''----------Start : User Model----------'''

class User(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    patientid=models.CharField(max_length=256,blank=True,null=True,editable=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    mobile=models.CharField(max_length=15,unique=True)
    family_members=models.JSONField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    selected = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}-{self.patientid}"

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

class PatientNotification(models.Model):
    patientid=models.ForeignKey(User,on_delete=models.PROTECT,blank=True)
    message=models.TextField()
    seen = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

'''----------End : User Model----------'''


'''----------Start : Doctor Model----------'''


class Department(models.Model):
    """
        This is department model.Example : Cardiologist,Neurologist,Dentist,etc.
    """
    id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
    name=models.CharField(max_length=100)
    img =models.FileField(upload_to='media/department/',null=True,blank=True)
    head=models.CharField(max_length=200,null=True,blank=True)
    enable = models.BooleanField(default=True) #Enable the service


    def __str__(self):
        return self.id

class CategorySpecialist(models.Model):
    """
        This model is of categorization. Example : Child Care, Women Care.
        And the department consists of specialisation like Cardiologist etc.
    """
    id=models.CharField(max_length=256, primary_key=True,unique=True,editable=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    depts = models.ManyToManyField(Department, blank=True)
    img =models.FileField(upload_to='media/categoryspecialist/',null=True,blank=True)

    def __str__(self):
        return self.id

class Doctor(models.Model):
    id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
    doctor_id=models.CharField(max_length=256,unique=True)
    email =models.EmailField(blank=True,unique=True)
    name=models.CharField(max_length=256)
    pin=models.CharField(max_length=5)
    age=models.PositiveIntegerField()
    gender=models.CharField(max_length=1)
    dob=models.DateField()
    experience=models.PositiveIntegerField()
    qualification=models.TextField()
    specialisation=models.TextField()
    languages_known=models.JSONField(default=dict,blank=True)
    modified_at=models.DateTimeField(editable=False)
    is_blocked = models.BooleanField(default=False)
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

class DoctorSchedule(models.Model):
        id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
        doctor_id=models.ForeignKey(Doctor,on_delete=models.CASCADE)
        schedule=models.JSONField(default=dict,blank=True)
        modified_at=models.DateTimeField(auto_now=True)
        created_at=models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return str(self.id)

class DoctorActivity(models.Model):
    doctor_id=models.ForeignKey(Doctor,on_delete=models.CASCADE,blank=True,null=True)
    login = models.JSONField(default=list,blank=True)
    logout = models.JSONField(default=list,blank=True)
    modified_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)
    stats=models.JSONField(default=dict,blank=True)

    def __str__(self):
        return str(self.doctor_id)


'''----------End : Doctor Model----------'''

'''----------Start: Patient Model----------'''
class Patient(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    primary = models.BooleanField(default=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    relation =models.CharField(max_length=256,null=True,blank=True)
    aadhar_id = models.CharField(max_length=256,null=True,blank=True)
    gender=models.CharField(max_length=256,null=True,blank=True)
    blood = models.CharField(max_length=255,null=True,blank=True)
    dob = models.CharField(max_length=255,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

'''----------end: Patient Model----------'''

'''----------Start : Carousel & promotional Model----------'''
class Carousel(models.Model):
    id = models.CharField(max_length=256, primary_key=True,unique=True,editable=False)
    img = models.FileField(upload_to='media/carousel/',null=True,blank=True)

class PromotionalSlider(models.Model):
    id = models.CharField(max_length=256, primary_key=True,unique=True,editable=False)
    img = models.FileField(upload_to='media/promotional/',null=True,blank=True)

class CategoryPromotion(models.Model):
    id = models.CharField(max_length=256, primary_key=True,unique=True)
    title = models.CharField(max_length=256, null=True,blank=True)
    category = models.ForeignKey(CategorySpecialist,on_delete=models.CASCADE,null=True,blank=True)

'''----------End : Carousel & promotional Model----------'''
  
'''----------Start : Appointment Model----------'''
class Appointment(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False) #TODO : setup signal to generate id
    offline = models.BooleanField(default=True)    
    date = models.CharField(max_length=256,null=True,blank=True)
    time = models.CharField(max_length=256,null=True,blank=True)
    doctor_id = models.CharField(max_length=256,null=True,blank=True)
    patient_id = models.CharField(max_length=256,null=True,blank=True)
    doctor = models.JSONField(default=dict,blank=True)
    patient = models.JSONField(default=dict,blank=True)
    timeline =models.JSONField(default=dict,blank=True)
    consulted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    reassigned = models.BooleanField(default=False)
    counter = models.JSONField(default=dict,blank=True)
    activity = models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)