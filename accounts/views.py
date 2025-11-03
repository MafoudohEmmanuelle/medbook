from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.urls import reverse
from django.conf import settings
from django.core.signing import Signer, BadSignature
# from django.core.mail import send_mail  # Uncomment for deployment

from .models import User, Doctor, Patient
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    DoctorProfileForm,
    LoginForm,
)

signer = Signer()



def switch_language(request):
    """Allows users to change language preference manually."""
    lang = request.GET.get('lang', 'en')
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return redirect(request.META.get('HTTP_REFERER', '/'))


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, _("Account created successfully! Please check your email to confirm."))

            # Uncomment this block when email sending is set up
            """
            token = signer.sign(user.email)
            confirm_url = request.build_absolute_uri(reverse('accounts:confirm_email', args=[token]))
            subject = _("Welcome to MedBook - Confirm your email")
            message = f"Hello {user.first_name},\n\nClick the link below to confirm your email:\n{confirm_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            """

            return redirect('accounts:login')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


"""
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

    # Option: Add email_verified flag here if model supports it
    login(request, user)
    translation.activate('en')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'en'
    return redirect('core:patient_dashboard')
"""


@login_required
def register_doctor(request):
    """Admin registers a doctor with basic info."""
    if not request.user.is_staff:
        messages.error(request, _("You are not authorized to access this page."))
        return redirect('core:home')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, _("Doctor registered successfully."))

            # Email sending (for deployment)
            """
            subject = _("Welcome to MedBook")
            message = _(
                f"Dear Dr. {doctor.first_name},\n\n"
                f"You have been registered on the MedBook platform.\n"
                f"Login with your email: {doctor.email}\n"
                f"Your temporary password has been assigned by the admin.\n\n"
                f"Please log in and complete your profile."
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [doctor.email])
            """

            return redirect('core:admin_dashboard')
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form})


@login_required
def complete_doctor_profile(request):
    """Allows a doctor to complete or update their profile."""
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

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            request.session['role'] = user.role
            if hasattr(user, 'preferred_language'):
                translation.activate(user.preferred_language)
                request.session[translation.LANGUAGE_SESSION_KEY] = user.preferred_language

            # Redirect based on user role
            if user.role == User.Role.PATIENT:
                return redirect('core:patient_dashboard')
            elif user.role == User.Role.DOCTOR:
                return redirect('core:doctor_dashboard')
            elif user.role == User.Role.ADMIN or user.is_staff:
                return redirect('core:admin_dashboard')
            else:
                messages.error(request, _("Invalid user role. Please contact support."))
                logout(request)
                return redirect('accounts:login')

        else:
            messages.error(request, _("Invalid email or password."))

    return render(request, "accounts/login.html")

@login_required
def logout_user(request):
    logout(request)
    messages.info(request, _("You have been logged out successfully."))
    return redirect('accounts:login')
