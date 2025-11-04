import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.urls import reverse
from django.core.signing import Signer, BadSignature

from .models import User, Doctor, Patient, Manager
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    DoctorProfileForm,
    LoginForm,
    ManagerCreationForm,
    ManagerProfileForm,
)
from .utils import send_account_email

signer = Signer()


def switch_language(request):
    lang = request.GET.get('lang', 'en')
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return redirect(request.META.get('HTTP_REFERER', '/'))


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            token = signer.sign(user.email)
            confirm_url = request.build_absolute_uri(reverse('accounts:confirm_email', args=[token]))
            send_account_email(user, confirm_url=confirm_url, role_label="Patient")

            messages.success(request, _("Account created successfully! Please check your email to confirm."))
            return redirect('accounts:login')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})

def confirm_email(request, token):
    try:
        email = signer.unsign(token)
    except BadSignature:
        messages.error(request, _("Invalid confirmation link."))
        return redirect('accounts:login')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, _("User not found."))
        return redirect('accounts:register_patient')

    login(request, user)
    translation.activate('en')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'en'
    return redirect('core:patient_dashboard')


@login_required
def register_doctor(request):
    if not request.user.is_staff:
        messages.error(request, _("You are not authorized to access this page."))
        return redirect('core:home')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user, temp_password = form.save()  # form returns both
            send_account_email(user, temp_password=temp_password, role_label="Doctor")
            messages.success(request, _("Doctor registered successfully. Credentials sent by email."))
            return redirect('core:admin_dashboard')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'accounts/register_doctor.html', {'form': form})


@login_required
def complete_doctor_profile(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated successfully."))
            return redirect('core:doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=doctor)
    return render(request, 'accounts/doctor_profile_form.html', {'form': form})


@login_required
def register_manager(request):
    if not request.user.is_staff:
        messages.error(request, _("You are not authorized to access this page."))
        return redirect('core:home')

    if request.method == 'POST':
        form = ManagerCreationForm(request.POST)
        if form.is_valid():
            user, temp_password = form.save()
            send_account_email(user, temp_password=temp_password, role_label="Manager")
            messages.success(request, _("Manager account created successfully. Credentials sent by email."))
            return redirect('core:admin_dashboard')
    else:
        form = ManagerCreationForm()
    return render(request, 'accounts/register_manager.html', {'form': form})

@login_required
def complete_manager_profile(request):
    manager = get_object_or_404(Manager, user=request.user)
    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, request.FILES, instance=manager)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated successfully."))
            return redirect('core:manager_dashboard')
    else:
        form = ManagerProfileForm(instance=manager)
    return render(request, 'accounts/manager_profile_form.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['role'] = user.role

            if hasattr(user, 'preferred_language'):
                translation.activate(user.preferred_language)
                request.session[translation.LANGUAGE_SESSION_KEY] = user.preferred_language

            # Redirect by role
            if user.role == User.Role.PATIENT:
                return redirect('core:patient_dashboard')
            elif user.role == User.Role.DOCTOR:
                return redirect('core:doctor_dashboard')
            elif user.role == User.Role.ADMIN or user.is_staff:
                return redirect('core:admin_dashboard')
            elif user.role == User.Role.MANAGER:
                return redirect('core:manager_dashboard')
            else:
                messages.error(request, _("Invalid user role. Please contact support."))
                logout(request)
                return redirect('accounts:login')
        else:
            messages.error(request, _("Invalid email or password."))
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_user(request):
    logout(request)
    messages.info(request, _("You have been logged out successfully."))
    return redirect('accounts:login')
