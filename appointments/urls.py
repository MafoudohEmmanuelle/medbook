from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('planning/create/', views.create_planning, name='create_planning'),
    path('doctor/unavailability/', views.mark_unavailability, name='mark_unavailability'),
    path('doctor/<int:doctor_id>/slots/', views.view_doctor_slots, name='view_doctor_slots'),
    path('slot/<int:slot_id>/book/', views.book_appointment, name='book_appointment'),
    path('doctor/appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:appointment_id>/done/', views.mark_done, name='mark_done'),
]
