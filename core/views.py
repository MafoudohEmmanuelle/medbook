from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.contrib import messages

from accounts.models import User, Doctor, Patient


def home(request):
    """
    Public landing page for the platform.
    Displays welcome message, login/register links, etc.
    """
    return render(request, 'core/home.html')

@login_required
def patient_dashboard(request):
    # Ensure only patients can access
    if request.user.role != User.Role.PATIENT:
        messages.error(request, _("Access denied: Patients only."))
        return redirect('core:home')

    patient = Patient.objects.filter(user=request.user).first()

    # Example: later connect these to Appointment model
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

    # Example placeholders for stats
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
def admin_dashboard(request):
    if not request.user.is_staff and request.user.role != User.Role.ADMIN:
        messages.error(request, _("Access denied: Administrators only."))
        return redirect('core:home')

    doctors = Doctor.objects.all()
    patients = Patient.objects.all()

    stats = {
        'total_doctors': doctors.count(),
        'total_patients': patients.count(),
    }

    context = {
        'doctors': doctors,
        'patients': patients,
        'stats': stats,
        'title': _("Admin Dashboard"),
    }
    return render(request, 'core/admin_dashboard.html', context)
