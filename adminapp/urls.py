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

    # --------------------------------- Department URLS ---------------------------------
    path("departments/", DepartmentsView.as_view(), name="department"),
    path("categoryspecialist/", CategorySpecialistView.as_view(), name="admin-categoryspecialist"),
    path("specialization-details/", SpecializationInDetail.as_view(), name="specialization-details"),
]