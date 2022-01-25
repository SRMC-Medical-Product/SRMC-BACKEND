from django.urls import path
from .doctor_views import *

urlpatterns=[

    path("login/",LoginDoctor.as_view(),name="modify-timings"),
    path("modify-timings/",ModifyDoctorTimings.as_view(),name="modify-timings")
]