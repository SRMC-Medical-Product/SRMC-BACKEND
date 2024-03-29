from django.urls import path
from .views import *
urlpatterns=[

    path('login-user/',LoginUser.as_view(),name="login-user"),
    path('register-user/',RegisterUser.as_view(),name="register-user"),
    path('validate-user/',ValidateUser.as_view(),name="validate-user"),
    
    path('profile/',UserProfile.as_view(),name="profile"),
    
    path('all-family-members/',FamilyMembers.as_view(),name="all-family-members"),

    path("home-screen/",HomeScreenAPI.as_view(),name="home-screen"),
    path("all-categories/",CategoriesScreen.as_view(),name="categories-screen"),
    path("patient-notification/",PatientNotificationScreen.as_view(),name="patient-notification"),

    path("search-results/",SearchResults.as_view(),name="search-results"),
]
