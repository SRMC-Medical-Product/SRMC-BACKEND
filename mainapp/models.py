from django.db import models

# Create your models here.
class User(models.Model):
    id=models.CharField(max_length=256,primary_key=True,unique=True,editable=False)
    name=models.CharField(max_length=256,null=True,blank=True)
    mobile=models.CharField(max_length=15,unique=True)
    aadhar_number=models.CharField(max_length=12,unique=True,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

class UserStatistics(models.Model):

    year=models.PositiveIntegerField()
    count=models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.id}{self.year}"