from django.urls import path
from .doctor_views import *

urlpatterns=[

    path("login/",LoginDoctor.as_view(),name="modify-timings"),
    path('change-pin/',ChangeDoctorPin.as_view(),name="change-pin"),    

    path("modify-timings/",ModifyDoctorTimings.as_view(),name="modify-timings"),
    path('doctor-profile-timings/',GetDoctorTimingsInProfile.as_view(),name="doctor-profile-timings"),
    path('doctor-profile/',DoctorProfile.as_view(),name="doctor-profile"),

    path('tickets/',DoctorTicketsScreen.as_view(),name="doctor-tickets"),
    path('notifications/',DoctorNotificationScreen.as_view(),name="doctor-notifications"),
    path('live-appointments/',LiveAppointment.as_view(),name="live-appointments"),
    path('history-appointments/',HistoryAppointment.as_view(),name="history-appointments"),

    path('procedure-medical/',ProcedureMedicalRecords.as_view(),name="procedure-medical"),
    path('medical-records/',AllMedicalRecords.as_view(),name="medical-records"),

    path('medical-records-appointments/',MedicalRecordsAppointments.as_view(),name="medical-records-appointments"),
    path('medical-reports/',AppointmentReport.as_view(),name="medical-reports"),
    path('all-patients/',AllPatients.as_view(),name="all-patients"),

    path('e-prescription/',ElectronicPrescription.as_view(),name="e-prescription"),

    path('test/',generate_pdf,name="test"),
    path('generate-prescription/',GenerateEPrescription.as_view(),name="generate-prescription"),
    
]