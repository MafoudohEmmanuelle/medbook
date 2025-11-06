from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Patient registration (logs in immediately after registration)
    path('register/patient/', views.register_patient, name='register_patient'),

    # Doctor registration (by admin or manager)
    path('register/doctor/', views.register_doctor, name='register_doctor'),

    # Manager registration (admin only)
    path('register/manager/', views.register_manager, name='register_manager'),

    # First-time login setup (password + profile completion)
    path('setup-account/', views.setup_account, name='setup_account'),

    # Profile updates after initial setup
    path('doctor/profile/', views.update_doctor_profile, name='update_doctor_profile'),
    path('manager/profile/', views.update_manager_profile, name='update_manager_profile'),

    # Language switch
    path('switch-language/', views.switch_language, name='switch_language'),
]
