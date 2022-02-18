from django.urls import path
from adminapp.views import *

urlpatterns = [

    # --------------------------------- Admin User URLS ---------------------------------
    path('login/' , AdminLogin.as_view() , name='admin-login'),
    path('register/' , AdminRegister.as_view() , name='admin-register'),
    path('all-get/' , AdminData.as_view() , name='admin-all-get'),
    path('user-get/' , AdminUserGet.as_view() , name='admin-user-get'),
    path('user-modify/' , AdminUserModify.as_view() , name='admin-user-modify'),
    path('user-password-modify/' , AdminUserPasswordModify.as_view() , name='admin-user-password-modify'),


    # --------------------------------- Promotions URLS ---------------------------------
    path('carousel/' , CarouselView.as_view() , name='carousel'),
    path('promotional-slider/' , PromotionalSliderView.as_view() , name='promotional-slider'),
    path('category-promotion/' , CategoryPromotionView.as_view() , name='category-promotion'),

    # --------------------------------- Department URLS ---------------------------------
    path("departments/", DepartmentsView.as_view(), name="department"),
    path("categoryspecialist/", CategorySpecialistView.as_view(), name="admin-categoryspecialist"),
    path("specialization-details/", SpecializationInDetail.as_view(), name="specialization-details"),

    # --------------------------------- Doctor URLS ---------------------------------
    path("doctor-get/", DoctorGet.as_view(), name="doctor-get"),
    path("doctor-details/", DoctorDetails.as_view(), name="doctor-details"),

    # --------------------------------- Doctor URLS ---------------------------------
    path("patient-get/", PatientGet.as_view(), name="patient-get"),
    path("patient-details/", PatientDetails.as_view(), name="patient-details"),

    # --------------------------------- Users data URLS ---------------------------------
    path("users-get/", UsersGet.as_view(), name="users-get"),

    # --------------------------------- Support Team URLS ---------------------------------
    path("help-desk/", HelpDeskTeam.as_view(), name="help-desk"), 
    
]