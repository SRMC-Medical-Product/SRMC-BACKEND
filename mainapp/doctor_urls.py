from django.urls import path
from .doctor_views import *

urlpatterns=[

    path("login/",LoginDoctor.as_view()),
]