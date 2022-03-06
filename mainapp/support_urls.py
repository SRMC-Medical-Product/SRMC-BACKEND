from django.urls import path
from .support_views import *


urlpatterns = [
    # --------------------------------- Login auth URLS ---------------------------------
    path('login-user/',LoginUser.as_view(),name="login-user"),
    path('logout-user/',LogoutUser.as_view(),name="logout-user"),

    # --------------------------------- Profile URLS ---------------------------------
    path('user-profile/' , UserProfile.as_view() , name='user-profile'),
    path('user-pin-update/' , UserPinModify.as_view() , name='user-pin-update'),

    # --------------------------------- Activity URLS ---------------------------------
    path('activity-log/' , ActivityLog.as_view() , name='activity-log'),

    # --------------------------------- Appointments URLS ---------------------------------
    path('appointments-history/', AppointmentsHistory.as_view() , name='appointments-history'),
    path('appointments-indetail/',InDetailAppointment.as_view() , name='appointments-indetail'),
    path('arrived-updated/',AppointmentUpdateArrived.as_view() , name='arrived-updated'),
    path('appointments-cancel/',AppointmentCancel.as_view() , name='appointments-cancel'),
    
    # --------------------------------- Doctor URLS ---------------------------------
    path('doctor-all-get/' , DoctorGet.as_view() , name='doctor-all-get'),
    path('doctor-indetail/' , DoctorDetails.as_view() , name='doctor-indetail'),
    
    # --------------------------------- Patient URLS ---------------------------------
    path('patient-all-get/' , PatientGet.as_view() , name='patient-all-get'),
    path('patient-indetail/' , PatientDetails.as_view() , name='patient-indetail'),

    # --------------------------------- Ticket URLS ---------------------------------
    path('patient-tickets/',AllPatientTickets.as_view() , name='patient-tickets'),
    path('patient-ticket-indetail/',PatientTicketDetails.as_view() , name='patient-ticket-indetail'),
    path('doctor-tickets/',AllDoctorTickets.as_view() , name='doctor-tickets'),
    path('doctor-ticket-indetail/',DoctorTicketDetails.as_view() , name='doctor-ticket-indetail'),

    # --------------------------------- Cancel all appointments URLS ---------------------------------
    path('cancel-all-appointments/',CancelAllAppointments.as_view() , name='cancel-all-appointments'),
    path('all-appointments/',GetAllAppointments.as_view() , name='all-appointments'),

    #---------------------------------Overview and Analytics--------------------
    path('overview-analytics/',OverviewAndAnalytics.as_view() , name='overview-analytics'),

    #---------------------------------Offline Appointment Bookingn--------------------
    path('checking-app-user/',CheckingAppuser.as_view() , name='checking-app-user'),
    path('offline-app-booking/',OfflineAppointmentBooking.as_view() , name='offline-app-booking'),
    path('all-depts/',AllDepartments.as_view() , name='all-depts'),
    path('dept-doctors/',DeptDoctors.as_view() , name='dept-doctors'),
    path('doctor-date-slot-details/',DoctorDateSlotDetails.as_view() , name='doctor-date-slot-details'),

]