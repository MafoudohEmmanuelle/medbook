from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone

from accounts.models import User, Doctor, Patient, Manager
from appointments.models import Appointment


def home(request):
    """
    Public landing page for the platform.
    Displays welcome message, login/register links, etc.
    """
    return render(request, 'core/home.html')


@login_required
def patient_dashboard(request):
    if request.user.role != User.Role.PATIENT:
        messages.error(request, _("Access denied: Patients only."))
        return redirect('core:home')

    patient = Patient.objects.filter(user=request.user).first()
    
    # Real appointment stats
    appointments = Appointment.objects.filter(patient=patient)
    stats = {
        'confirmed': appointments.filter(status='confirmed').count(),
        'pending': appointments.filter(status='modified').count(),  # modify as needed
        'cancelled': appointments.filter(status='cancelled').count(),
        'completed': appointments.filter(status='completed').count(),
    }

    context = {
        'patient': patient,
        'stats': stats,
        'title': _("Patient Dashboard"),
    }
    return render(request, 'core/patient_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    if request.user.role != User.Role.DOCTOR:
        messages.error(request, _("Access denied: Doctors only."))
        return redirect('core:home')

    doctor = Doctor.objects.filter(user=request.user).first()
    today = timezone.localdate()

    appointments = Appointment.objects.filter(doctor=doctor)
    stats = {
        'appointments_today': appointments.filter(time_slot__date=today).count(),
        'pending_approvals': appointments.filter(status='pending').count(),  # adjust if needed
        'patients_seen': appointments.filter(status='completed').count(),
    }

    context = {
        'doctor': doctor,
        'stats': stats,
        'title': _("Doctor Dashboard"),
    }
    return render(request, 'core/doctor_dashboard.html', context)

@login_required
def manager_dashboard(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(request, _("Access denied: Managers only."))
        return redirect('core:home')

    # Fetch counts
    active_patients_count = Patient.objects.count()
    active_doctors_count = Doctor.objects.count()
    # Example: pending requests can be appointments with status 'pending'
    pending_requests_count = Appointment.objects.filter(status='pending').count()
    # Completed tasks could be completed appointments
    completed_tasks_count = Appointment.objects.filter(status='completed').count()

    # Managers list
    managers = Manager.objects.all()  # or filter active managers if needed

    context = {
        'active_patients_count': active_patients_count,
        'active_doctors_count': active_doctors_count,
        'pending_requests_count': pending_requests_count,
        'completed_tasks_count': completed_tasks_count,
        'managers': managers,
        'title': _("Manager Dashboard"),
    }
    return render(request, 'core/manager_dashboard.html', context)