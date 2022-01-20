from django.urls import path
from .views import *
urlpatterns=[

    path('login-user/',LoginUser.as_view(),name="login"),
    path('validate-user/',ValidateUser.as_view(),name="validate"),
    path('profile/',UserProfile.as_view(),name="profile"),

]
