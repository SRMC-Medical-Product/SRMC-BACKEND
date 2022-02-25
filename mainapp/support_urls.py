from django.urls import path
from .support_views import *


urlpatterns = [
    # --------------------------------- Login auth URLS ---------------------------------
    path('login-user/',LoginUser.as_view(),name="login-user"),
    path('logout-user/',LogoutUser.as_view(),name="logout-user"),

    # --------------------------------- Profile URLS ---------------------------------
    path('user-profile/' , UserProfile.as_view() , name='user-profile'),
    path('user-pin-update/' , UserPinModify.as_view() , name='user-pin-update'),

    # --------------------------------- Activity URLS ---------------------------------
    path('activity-log/' , ActivityLog.as_view() , name='activity-log'),

    # --------------------------------- Appointments URLS ---------------------------------
    path('appointments-history/', AppointmentsHistory.as_view() , name='appointments-history'),
    path('appointments-indetail/',InDetailAppointment.as_view() , name='appointments-indetail'),

    # --------------------------------- Doctor URLS ---------------------------------
    path('doctor-all-get/' , DoctorGet.as_view() , name='doctor-all-get'),
    path('doctor-indetail/' , DoctorDetails.as_view() , name='doctor-indetail'),
    
    # --------------------------------- Patient URLS ---------------------------------
    path('patient-all-get/' , PatientGet.as_view() , name='patient-all-get'),
    path('patient-indetail/' , PatientDetails.as_view() , name='patient-indetail'),

    # --------------------------------- Departments URLS ---------------------------------
    path('departments/' , DepartmentsView.as_view() , name='departments'),
    path('specilization/' , SpecializationInDetail.as_view() , name='specilization'),
 

]