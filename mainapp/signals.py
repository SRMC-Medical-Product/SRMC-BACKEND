from time import time
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from datetime import timedelta
import random
import uuid

@receiver(pre_save,sender=User)
def create_user_id(sender,instance,**kwargs):
    """
        signal to generate the user id

    """
    if instance.id in ["",None]:
        year=timezone.now().year
        user_count=UserStatistics.objects.get_or_create(year=year)[0]
        str_count=str(user_count.count)

        zeros="0"*(9-len(str_count))

        instance.id=f"{year}"+zeros+str_count

        user_count.count=user_count.count+1
        user_count.save(update_fields=['count'])


@receiver(pre_save,sender=Patient)
def create_patient_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = Patient.objects.count()
        id = str(uuid.uuid4())[:7] + str(count+1)[:1]
        pat=Patient.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:7] + str(count+1)[:1]
        instance.id=id     

@receiver(pre_save,sender=UserOtp)
def create_otp_secret(sender,instance,**kwargs):
    """
        signal responsible to generate otp and secret code for a particular user

    """
    if instance.otp in ["",None] or instance.secret in ["",None]:
        otp=""
        for _ in range(6):
            digit=random.randint(0,9)
            otp=otp+str(digit)
        
        instance.otp=otp

        secret=""
        for _ in range(10):
            ink=random.randint(1,2)
            if ink==1:
                digit=chr(random.randint(65,90))
                secret=secret+digit
            else:
                digit=random.randint(0,9)
                secret=secret+str(digit)
        
        instance.code=secret
        instance.expiry_time=timezone.now()+timedelta(minutes=3)


@receiver(pre_save,sender=Doctor)
def generate_doctor_id(sender,instance,**kwargs):
    """
        presave signal to generate doctor id

    """
    if instance.id in [None,""]:
        id=""
        for _ in range(10):
            ink=random.randint(1,2)
            if ink==1:
                digit=chr(random.randint(65,90))
                id=id+digit
            else:
                digit=random.randint(0,9)
                id=id+str(digit)
        
        while len(Doctor.objects.filter(id=id))!=0:
            id=""
            for _ in range(10):
                ink=random.randint(1,2)
                if ink==1:
                    digit=chr(random.randint(65,90))
                    id=id+digit
                else:
                    digit=random.randint(0,9)
                    id=id+str(digit)
        
        instance.id=id

        
        
        
    
    instance.modified_at=timezone.now()


@receiver(pre_save,sender=Department)
def generate_department_id(sender,instance,**kwargs):

    """
        presave signal to generate department if in hospital
    
    """
    if instance.id in [None,""]:

        name3=instance.name[:3]
        name3_=instance.name[-1:-4:-1]         
        id=name3.upper()+name3_.upper()+str(random.randint(1000,9999))
        while len(Department.objects.filter(id=id))!=0:
            id=name3.upper()+name3_.upper()+str(random.randint(1000,9999))
        instance.id=id

@receiver(pre_save,sender=DoctorTimings)
def update_modified_at(sender,instance,**kwargs):

    instance.modified_at=timezone.now()


@receiver(pre_save,sender=Carousel)
def create_carousel_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = Carousel.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=Carousel.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
            pat=Carousel.objects.filter(id=id)
        instance.id=id 

@receiver(pre_save,sender=PromotionalSlider)
def create_slider_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = PromotionalSlider.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=PromotionalSlider.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
            pat=PromotionalSlider.objects.filter(id=id)
        instance.id=id 

@receiver(pre_save,sender=CategoryPromotion)
def create_promotion_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = CategoryPromotion.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=CategoryPromotion.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
            pat=CategoryPromotion.objects.filter(id=id)
        instance.id=id 

@receiver(pre_save,sender=CategorySpecialist)
def create_category_specialist_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = CategorySpecialist.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=CategorySpecialist.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        instance.id=id 

@receiver(pre_save,sender=Appointment)
def create_appointment_id(sender,instance,**kwargs):
    #TODO : change appointment id format
    if instance.id in [None,""]:
        count = Appointment.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=Appointment.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
            pat=Appointment.objects.filter(id=id)
        instance.id=id 

@receiver(pre_save,sender=HelpDeskUser)
def create_help_desk_user_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = HelpDeskUser.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=HelpDeskUser.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        instance.id=id 


@receiver(pre_save,sender=Medicines)
def create_medicine_id(sender,instance,**kwargs):
    if instance.id in [None,""]:
        count = Medicines.objects.count()
        id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        pat=Medicines.objects.filter(id=id)
        while pat.exists():
            id = str(uuid.uuid4())[:5] + str(count+1)[:1]
        instance.id=id 

@receiver(pre_save,sender=PatientTickets)
def create_medicine_id(sender,instance,**kwargs):
    if instance.id in ["",None]:
        year=timezone.now().year
        ticket_count=PatientTickets.objects.count()
        zeros="0"*(9-len(str(ticket_count)))
        instance.id=f"{year}"+zeros+str(ticket_count)

@receiver(pre_save,sender=DoctorTickets)
def create_medicine_id(sender,instance,**kwargs):
    if instance.id in ["",None]:
        year=timezone.now().year
        ticket_count=DoctorTickets.objects.count()
        zeros="0"*(9-len(str(ticket_count)))
        instance.id=f"{year}"+zeros+str(ticket_count)
