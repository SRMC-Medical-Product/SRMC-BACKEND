from django.urls import path
from .views import *
urlpatterns=[

    path('login-user/',LoginUser.as_view(),name="login"),
    path('validate-user/',ValidateUser.as_view(),name="validate"),
    path('profile/',UserProfile.as_view(),name="profile"),
    path("add-family/",AddFamilyMember.as_view(),name="add-family"),
    
    path("home-screen/",HomeScreenAPI.as_view(),name="home-screen"),
    path("all-categories/",CategoriesScreen.as_view(),name="categories-screen"),
    path("patient-notification/",PatientNotificationScreen.as_view(),name="patient-notification"),
]
