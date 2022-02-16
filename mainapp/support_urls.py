from django.urls import path
from .support_views import *


urlpatterns = [
    # --------------------------------- Login auth URLS ---------------------------------
    path('login-user/',LoginUser.as_view(),name="login-user"),

    # --------------------------------- Departments URLS ---------------------------------
    path('departments/' , DepartmentsView.as_view() , name='departments'),
    path('specilization/' , SpecializationInDetail.as_view() , name='specilization'),

    # --------------------------------- Appointments URLS ---------------------------------
    path('appointments-history/' , AppointmentsHistory.as_view() , name='appointments-history'),
    
    
    # --------------------------------- Doctor URLS ---------------------------------
    path('doctor-all-get/' , DoctorGet.as_view() , name='doctor-all-get'),
    path('doctor-indetail/' , DoctorDetails.as_view() , name='doctor-indetail'),
 
    # --------------------------------- Patient URLS ---------------------------------
    path('patient-all-get/' , PatientGet.as_view() , name='patient-all-get'),
    path('patient-indetail/' , PatientDetails.as_view() , name='patient-indetail'),

]