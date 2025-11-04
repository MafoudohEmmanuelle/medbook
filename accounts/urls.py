from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('switch-language/', views.switch_language, name='switch_language'),
    path('doctor/profile/', views.complete_doctor_profile, name='complete_doctor_profile'),
    path('confirm-email/<str:token>/', views.confirm_email, name='confirm_email'),
    path('register/manager/', views.register_manager, name='register_manager'),
    path('manager/profile/', views.complete_manager_profile, name='complete_manager_profile'),
]
