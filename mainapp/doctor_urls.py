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
    path('appointment-indetail/',AppointmentInDetail.as_view(),name="appointment-indetail"),

    path('create-procedure-medical/',ProcedureMedicalRecords.as_view(),name="procedure-medical"),
    path('medical-records/',AllMedicalRecords.as_view(),name="medical-records"),

    path('medical-records-appointments/',MedicalRecordsAppointments.as_view(),name="medical-records-appointments"),
    path('medical-reports/',AppointmentReport.as_view(),name="medical-reports"),
    path('patient-all-reports/',PatientAllReports.as_view(),name="patient-all-reports"),
    
    path('all-patients/',AllPatients.as_view(),name="all-patients"),

    path('e-prescription/',ElectronicPrescription.as_view(),name="e-prescription"),
    path('generate-prescription/',GenerateEPrescription.as_view(),name="generate-prescription"),
    path('view-drugs/',AllMedicinesDrugs.as_view(),name="view-drugs"),

    path('appointment-consulted/',AppointmentConsulted.as_view(),name="appointment-consulted"),    

    path('analytics/',AppointmentAnalytics.as_view(),name="analytics"),
    path('weekly-analytics/',WeeklyAppointmentAnalytics.as_view(),name="weekly-analytics"),

    path('home-screen/',HomeScreen.as_view(),name="home-screen"),

]