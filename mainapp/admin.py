from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(UserStatistics)
admin.site.register(UserOtp)
admin.site.register(Doctor)
admin.site.register(Department)
admin.site.register(DoctorTimings)
admin.site.register(DoctorSchedule)
admin.site.register(Carousel)
admin.site.register(PromotionalSlider)
admin.site.register(CategorySpecialist)
admin.site.register(PatientNotification)
admin.site.register(Patient)
admin.site.register(CategoryPromotion)
admin.site.register(DoctorActivity)
admin.site.register(Appointment)
admin.site.register(HelpDeskUser)
admin.site.register(HelpDeskAppointment)
admin.site.register(PatientTickets)
admin.site.register(DoctorTickets)