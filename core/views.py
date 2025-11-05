from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from accounts.models import User, Doctor, Patient
from appointments.models import Appointment  # Assuming you have an Appointment model


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

    stats = {
        'confirmed': 2,
        'pending': 1,
        'cancelled': 0,
        'completed': 4,
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

    stats = {
        'appointments_today': 5,
        'pending_approvals': 3,
        'patients_seen': 18,
    }

    context = {
        'doctor': doctor,
        'stats': stats,
        'title': _("Doctor Dashboard"),
    }
    return render(request, 'core/doctor_dashboard.html', context)


@login_required
def manager_dashboard(request):
    """
    Dashboard view for Managers.
    Shows overview stats and a table of doctors.
    """
    if request.user.role != User.Role.MANAGER:
        messages.error(request, _("Access denied: Managers only."))
        return redirect('core:home')

    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    appointments = Appointment.objects.all()  # Replace with your Appointment queryset if exists

    stats = {
        'total_doctors': doctors.count(),
        'total_patients': patients.count(),
        'active_appointments': appointments.filter(status='active').count(),
        'completed_appointments': appointments.filter(status='completed').count(),
    }

    context = {
        'doctors': doctors,
        'patients': patients,
        'stats': stats,
        'title': _("Manager Dashboard"),
    }
    return render(request, 'core/manager_dashboard.html', context)
