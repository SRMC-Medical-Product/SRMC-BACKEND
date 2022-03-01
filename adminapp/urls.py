from django.urls import path
from adminapp.views import *

urlpatterns = [

    # --------------------------------- Admin User URLS ---------------------------------
    path('login/' , AdminLogin.as_view() , name='admin-login'),
    path('all-get/' , AdminData.as_view() , name='admin-all-get'),
    path('user-get/' , AdminUserGet.as_view() , name='admin-user-get'),
    path('user-modify/' , AdminUserModify.as_view() , name='admin-user-modify'),
    path('user-password-modify/' , AdminUserPasswordModify.as_view() , name='admin-user-password-modify'),
    

    # --------------------------------- Promotions URLS ---------------------------------
    path('carousel/' , CarouselView.as_view() , name='carousel'),
    path('promotional-slider/' , PromotionalSliderView.as_view() , name='promotional-slider'),
    path('category-promotion/' , CategoryPromotionView.as_view() , name='category-promotion'),

    # --------------------------------- Department URLS ---------------------------------
    path("departments/", DepartmentsView.as_view(), name="department"),
    path("categoryspecialist/", CategorySpecialistView.as_view(), name="admin-categoryspecialist"),

    # --------------------------------- Doctor URLS ---------------------------------
    path('doctor-create/',DoctorCreate.as_view(),name='admin-doctor-create'),
    path('doctor-update/',DoctorProfileUpdate.as_view(),name='admin-doctor-update'),
    path('doctor-all-get/' , DoctorGet.as_view() , name='doctor-all-get'),
    path('doctor-indetail/' , DoctorDetails.as_view() , name='doctor-indetail'),
    path('department-doctors/',DepartmentDoctors.as_view() , name='department-doctors'),
        
    # --------------------------------- Patient URLS ---------------------------------
    path('patient-all-get/' , PatientGet.as_view() , name='patient-all-get'),
    path('patient-indetail/' , PatientDetails.as_view() , name='patient-indetail'),

    # --------------------------------- Users data URLS ---------------------------------
    path("patient-app-users/", PatientAppUsers.as_view(), name="patient-app-users"),

    # --------------------------------- Support Team URLS ---------------------------------
    path("help-desk/", HelpDeskTeam.as_view(), name="help-desk"), 
    path('help-desk-details/',HelpDeskUserDetails.as_view(), name='help-desk-details'),

    # ------------------------------Block / Access User URLS ------------------------------
    path('access-help-desk/',AccessHelpDeskUser.as_view(), name='access-help-desk'),
    path('access-doctor/',AccessDoctorUser.as_view(), name='access-doctor'),

    # --------------------------------- Appointment URLS ---------------------------------
    path('get-appointments/',GetAllAppointments.as_view() , name='get-all-appointments'),

    # --------------------------------- Ticket URLS ---------------------------------
    path('patient-tickets/',AllPatientTickets.as_view() , name='patient-tickets'),
    path('doctor-tickets/',AllDoctorTickets.as_view() , name='doctor-tickets'),

    #-------------------------Analytics --------------------------------
    path('analytics/',Analytics.as_view() , name='analytics'),

    # --------------------------------- Drugs URLS ---------------------------------
    path('all-medicine-drugs/',AllMedicinesDrugs.as_view() , name='all-medicine-drugs'),
    path('bulk-upload-drugs/',BulkUploadMedicines.as_view() , name='bulk-upload-drugs'),

]