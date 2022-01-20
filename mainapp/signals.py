from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from datetime import timedelta
import random

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


