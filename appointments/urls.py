from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    # Manager URLs
    path('generate-global-planning/', views.generate_global_planning, name='generate_global_planning'),
    path('manager-planning/', views.manager_planning, name='manager_planning'),
    path('add-doctor-unavailability/', views.add_doctor_unavailability, name='add_doctor_unavailability'),

    # Doctor URLs
    path('doctor-appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('update-appointment/<int:appointment_id>/<str:action>/', views.update_appointment_status, name='update_appointment_status'),

    # Patient URLs
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('book-appointment/<int:doctor_id>/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('doctor-schedule/<int:doctor_id>/', views.view_doctor_schedule, name='view_doctor_schedule'),

    # Slot management
    path('block-slot/<int:slot_id>/', views.block_slot, name='block_slot'),      # We'll need this view
    path('unblock-slot/<int:slot_id>/', views.unblock_slot, name='unblock_slot'),# We'll need this view
]
