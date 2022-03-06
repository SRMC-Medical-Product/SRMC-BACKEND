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

    path('doctors-slots/',DoctorSlotDetails.as_view(),name="doctors-slots"),
    
    path('change-member-booking/',BookingChangeMember.as_view(),name="change-member-booking"),

    path('appointment-history/',AppointmentHistory.as_view(),name="appointment-history"),
    path('appointment-pending/',PendingAppointment.as_view(),name="appointment-pending"),
    path('appointment-indetail/',AppointmentInDetail.as_view(),name="appointment-indetail"),

    path('book-appointment/',BookAppoinment.as_view(),name="book-appoinment"),
    path('appointment-confirm/',ConfirmationScreen.as_view(),name="appointment-confirm"),
    path('appointment-cancel/',AppointmentCancel.as_view(),name="appointment-cancel"),

    path('patient-tickets/',PatientTicketsIssues.as_view(),name="patient-tickets"),

    path('family-medical-records/',FamilyMedicalRecord.as_view(),name="family-medical-records"),
    path('procedural-records/',PatientProceduralRecord.as_view(),name="procedural-records"),
    path('display-medical-records/',DisplayMedicalRecords.as_view(),name="display-medical-records"),
    path('display-appointment-records/',DisplayAppointmentMedicalRecords.as_view(),name="display-appointment-records"),

]
