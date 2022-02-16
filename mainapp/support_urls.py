from django.urls import path
from .support_views import *

urlpatterns=[
    path('login-user/',LoginUser.as_view(),name="login-user"),
]