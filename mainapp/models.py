from django.db import models


'''----------Start : User Model----------'''
class SuperAdmin(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    name = models.CharField(max_length=256,null=True,blank=True)
    email = models.CharField(max_length=256,null=True,blank=True,unique=True)
    password = models.CharField(max_length=256,null=True,blank=True)
    phone = models.CharField(max_length=256,null=True,blank=True,unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}-{self.id}"


class User(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    patientid=models.CharField(max_length=256,blank=True,null=True,editable=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    mobile=models.CharField(max_length=15,unique=True)
    family_members=models.JSONField(null=True,blank=True)
    img =models.FileField(upload_to='media/patient/',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    selected = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}-{self.patientid}-{self.mobile}"

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
"""
    counter[json] = [
        {
            "id": "id",
            "counter": "counter",
            "floor": "floor",
            "created_at": "created_at"
        }
    ]
"""

class Department(models.Model):
    """
        This is department model.Example : Cardiologist,Neurologist,Dentist,etc.
    """
    id=models.CharField(max_length=256,unique=True,primary_key=True,editable=False)
    name=models.CharField(max_length=100)
    img =models.FileField(upload_to='media/department/',null=True,blank=True)
    head=models.CharField(max_length=200,null=True,blank=True)
    counter = models.JSONField(default=dict,null=True,blank=True)
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
    phone = models.CharField(max_length=15,null=True,blank=True)
    doctor_id=models.CharField(max_length=256,unique=True)
    email =models.EmailField(blank=True,unique=True)
    name=models.CharField(max_length=256)
    profile_img = models.FileField(upload_to='media/doctor/',null=True,blank=True)
    pin=models.CharField(max_length=512)
    age=models.PositiveIntegerField()
    gender=models.CharField(max_length=1)
    dob=models.DateField()
    experience=models.PositiveIntegerField()
    qualification=models.TextField()
    specialisation=models.TextField()
    languages_known=models.JSONField(default=dict,blank=True,null=True)
    modified_at=models.DateTimeField(editable=False)
    is_blocked = models.BooleanField(default=False)
    department_id=models.ForeignKey(Department,null=True,on_delete=models.SET_NULL)
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}-{self.department_id.name}"

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

class DoctorActivity(models.Model):
    doctor_id=models.ForeignKey(Doctor,on_delete=models.CASCADE,blank=True,null=True)
    login = models.JSONField(default=list,blank=True)
    logout = models.JSONField(default=list,blank=True)
    modified_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)
    stats=models.JSONField(default=dict,blank=True)

    def __str__(self):
        return str(self.doctor_id)

class DoctorNotification(models.Model):
    doctor_id=models.ForeignKey(Doctor,on_delete=models.CASCADE,blank=True)
    message=models.TextField()
    seen = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

'''----------End : Doctor Model----------'''

'''----------Start: Patient Model----------'''
class Patient(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    img =models.FileField(upload_to='media/patient/',null=True,blank=True)
    primary = models.BooleanField(default=False)
    appuser = models.CharField(max_length=256,null=True,blank=True)
    name=models.CharField(max_length=256,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    relation =models.CharField(max_length=256,null=True,blank=True)
    aadhar_id = models.CharField(max_length=256,null=True,blank=True)
    gender=models.CharField(max_length=256,null=True,blank=True)
    blood = models.CharField(max_length=255,null=True,blank=True)
    dob = models.CharField(max_length=255,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.appuser} - {self.name}"

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
"""
    timeline format : {
        "step1":{
            "title" : "Booking Confirmed",
            "time" : "HMS format",
            "completed" : bool
        },
        "step2":{
            "title" : "Arrived at Hospital",
            "time" : "HMS format",
            "completed" : bool
        },
        "step3":{
            "title" : "Consulted",
            "time" : "HMS format",
            "completed" : bool
        },
        "cancel":{
            "title" : "Cancelled",
            "time" : "HMS format",
            "completed" : bool
        }
    }
    counter_format = [
        {
            "id": "c1",
            "floor" : "1"
        }
    ]
"""

class Appointment(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False) #TODO : setup signal to generate id
    offline = models.BooleanField(default=True)    
    date = models.DateField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True)
    doctor_id = models.CharField(max_length=256,null=True,blank=True)
    patient_id = models.CharField(max_length=256,null=True,blank=True)
    dept_id = models.CharField(max_length=256,null=True,blank=True)
    doctor = models.JSONField(default=dict,blank=True)
    patient = models.JSONField(default=dict,blank=True)
    timeline =models.JSONField(null=True,blank=True)
    consulted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    reassigned = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    counter = models.JSONField(default=dict,blank=True)
    activity = models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)

'''----------End : Appointment Model----------'''

'''----------Start : HelpDesk Model----------'''
"""
    json_format : [activity] {
        "login" : [],
        "logout" : [],
        "log" : [],
    }
"""
class HelpDeskUser(models.Model):
    id =models.CharField(max_length=256,primary_key=True,unique=True,editable=False) 
    name = models.CharField(max_length=256,null=True,blank=True)
    email = models.EmailField(null=True,blank=True,unique=True)
    mobile = models.CharField(max_length=256,null=True,blank=True,unique=True)
    pin = models.CharField(max_length=256,null=True,blank=True)
    is_blocked = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)
    specialisation=models.ManyToManyField(Department,blank=True)
    activity=models.JSONField(default=dict,blank=True)

    def __str__(self):
        return f"{str(self.id)}"

class HelpDeskAppointment(models.Model):
    department = models.ForeignKey(Department,on_delete=models.PROTECT,null=True,blank=True,related_name="help_desk_user")
    date = models.DateField(null=True,blank=True)
    count = models.PositiveIntegerField(default=0)
    bookings = models.JSONField(default=list,blank=True)
    consulted =models.JSONField(default=dict,blank=True)
    missing = models.JSONField(default=dict,blank=True)
    reassign = models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{str(self.department)} - {self.date}"


'''----------End : HelpDesk Model----------'''

'''----------Start : Medicines Model----------'''

class Medicines(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    name = models.CharField(max_length=256,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)    

'''----------End : Medicines Model----------'''

'''----------Start : Tickets/Issues Model----------'''
class PatientTickets(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    dept = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    admin_id = models.ForeignKey(HelpDeskUser,on_delete=models.CASCADE,null=True,blank=True)
    closed = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True) 
    issues = models.JSONField(default=dict,blank=True)

    def __str__(self):
        return str(self.id)

class DoctorTickets(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    doctor_id = models.ForeignKey(Doctor,on_delete=models.CASCADE,null=True,blank=True)
    dept = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    admin_id = models.ForeignKey(HelpDeskUser,on_delete=models.CASCADE,null=True,blank=True)
    closed = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True) 
    issues = models.JSONField(default=dict,blank=True)

    def __str__(self):
        return str(self.id)

'''----------End : Tickets/Issues Model----------'''

'''----------Start : Medical Records Model----------'''
"""
    json_format:
    "" : "",
    records : [
        {
            "deptid": "id",
            "deptname" : "name",
            "created_at" : "date",
            "records" : [
                {
                    "Patient" : "id",
                    "doctorname" : "",
                    "created_at" : "date",
                    "date" : "appointmentdate",
                    "files" : [
                        {
                            "type" : "pdf",
                            "url" : "url"
                            "name" : "name",
                            "username" : "name",
                            "userid":"",
                            "user":"",
                            "created_at" : "date"
                        }
                    ]
                }
            ]
        }
    ]
"""
class MedicalRecords(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    patientid = models.CharField(max_length=256,null=True,blank=True)
    title = models.CharField(max_length=256,null=True,blank=True)
    records = models.JSONField(default=list,blank=True)
    created_by = models.CharField(max_length=256,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

"""
    Json_format of records : {
        "title": "e-prescription-title",
        "created_at": "date",
        medicines : [
            {
                "medicineid" : "id",
                "name": "tablet name",
                "mrng": bool,
                "noon": bool,
                "evening": bool,
                "night": bool,
                "beforefood" : bool,
                "afterfood" : bool,
                "quantity": "30",
                "duration": "in days"
            }
        ]
    }
"""
class MedicalPrescriptions(models.Model):
    id = models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    patientid = models.CharField(max_length=256,null=True,blank=True)
    appointmentid = models.CharField(max_length=256,null=True,blank=True)
    doctorid = models.CharField(max_length=256,null=True,blank=True)
    records = models.JSONField(default=dict,blank=True)
    generated = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

'''----------End : Medical Records Model----------'''

'''----------Start : Medicines Model----------'''
class Drugs(models.Model):
    name = models.CharField(max_length=512,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
