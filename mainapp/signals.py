from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone

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
