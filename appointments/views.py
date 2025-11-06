from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from .models import User, Doctor, Patient, Manager
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    DoctorProfileForm,
    ManagerCreationForm,
    ManagerProfileForm,
    EmailOnlyLoginForm,
    DefinePasswordForm,
)

# --- Language switching ---
def switch_language(request):
    lang = request.GET.get('lang', 'en')
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return redirect(request.META.get('HTTP_REFERER', '/'))


# --- Patient registration ---
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Account created successfully!"))
            return redirect('core:patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})


# --- Login view ---
def login_view(request):
    if request.method == 'POST':
        form = EmailOnlyLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, _("Email not found."))
                return redirect('accounts:login')

            if not user.has_usable_password():
                # First-time login (doctor/manager)
                login(request, user)
                return redirect('accounts:setup_account')
            else:
                # Normal login — require password
                user_auth = authenticate(request, email=email, password=request.POST.get('password'))
                if user_auth:
                    login(request, user_auth)
                else:
                    messages.error(request, _("Invalid credentials."))
                    return redirect('accounts:login')

            # Redirect by role
            if user.role == User.Role.PATIENT:
                return redirect('core:patient_dashboard')
            elif user.role == User.Role.DOCTOR:
                return redirect('core:doctor_dashboard')
            elif user.role == User.Role.MANAGER:
                return redirect('core:manager_dashboard')
            elif user.role == User.Role.ADMIN or user.is_staff:
                return redirect('/admin/')
            else:
                messages.error(request, _("Invalid user role."))
                logout(request)
                return redirect('accounts:login')
    else:
        form = EmailOnlyLoginForm()
    return render(request, "accounts/login.html", {"form": form})


# --- First-time setup for doctor/manager ---
@login_required
def setup_account(request):
    user = request.user
    if user.has_usable_password():
        # Already set up, redirect to their dashboard
        if user.role == User.Role.DOCTOR:
            return redirect('core:doctor_dashboard')
        elif user.role == User.Role.MANAGER:
            return redirect('core:manager_dashboard')
        return redirect('core:home')

    # Setup mode (first login)
    if user.role == User.Role.DOCTOR:
        profile_instance = get_object_or_404(Doctor, user=user)
        ProfileForm = DoctorProfileForm
        dashboard_redirect = 'core:doctor_dashboard'
    elif user.role == User.Role.MANAGER:
        profile_instance = get_object_or_404(Manager, user=user)
        ProfileForm = ManagerProfileForm
        dashboard_redirect = 'core:manager_dashboard'
    else:
        messages.error(request, _("You cannot access setup page."))
        return redirect('accounts:login')

    if request.method == 'POST':
        password_form = DefinePasswordForm(user, request.POST)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile_instance)
        if password_form.is_valid() and profile_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, user)
            profile_form.save()
            messages.success(request, _("Setup completed successfully!"))
            return redirect(dashboard_redirect)
    else:
        password_form = DefinePasswordForm(user)
        profile_form = ProfileForm(instance=profile_instance)

    return render(request, 'accounts/setup_account.html', {
        'password_form': password_form,
        'profile_form': profile_form
    })


# --- Doctor registration (by admin/manager) ---
@login_required
def register_doctor(request):
    if request.user.role not in [User.Role.ADMIN, User.Role.MANAGER]:
        messages.error(request, _("You are not authorized to access this page."))
        return redirect('core:home')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Doctor registered successfully. First login will require setup."))
            return redirect('core:manager_dashboard' if request.user.role == User.Role.MANAGER else 'core:admin_dashboard')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'accounts/register_doctor.html', {'form': form})


# --- Manager registration (by admin) ---
@login_required
def register_manager(request):
    if request.user.role != User.Role.ADMIN:
        messages.error(request, _("You are not authorized to access this page."))
        return redirect('core:home')

    if request.method == 'POST':
        form = ManagerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Manager registered successfully. First login will require setup."))
            return redirect('core:admin_dashboard')
    else:
        form = ManagerCreationForm()
    return render(request, 'accounts/register_manager.html', {'form': form})


# --- Profile updates ---
@login_required
def update_doctor_profile(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    form = DoctorProfileForm(request.POST or None, request.FILES or None, instance=doctor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Your profile has been updated successfully."))
        return redirect('core:doctor_dashboard')
    return render(request, 'accounts/doctor_profile_form.html', {'form': form})


@login_required
def update_manager_profile(request):
    manager = get_object_or_404(Manager, user=request.user)
    form = ManagerProfileForm(request.POST or None, request.FILES or None, instance=manager)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Your profile has been updated successfully."))
        return redirect('core:manager_dashboard')
    return render(request, 'accounts/manager_profile_form.html', {'form': form})


# --- Logout ---
@login_required
def logout_user(request):
    logout(request)
    messages.info(request, _("You have been logged out successfully."))
    return redirect('accounts:login')
