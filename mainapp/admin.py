from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(UserStatistics)
admin.site.register(UserOtp)
admin.site.register(Doctor)
admin.site.register(Department)