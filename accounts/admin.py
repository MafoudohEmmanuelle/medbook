from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.urls import reverse

from .models import User, Doctor, Patient, Manager
from .forms import DoctorRegistrationForm, ManagerCreationForm
from .utils import send_account_email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'address', 'profile_image', 'gender', 'date_of_birth')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Role'), {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin interface for creating and managing doctors."""
    list_display = ('user', 'specialty', 'years_of_experience')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        """If new doctor, generate temp password and send welcome email."""
        if not change:  # Only when creating
            temp_password = get_random_string(8)
            user = obj.user
            user.set_password(temp_password)
            user.role = User.Role.DOCTOR
            user.save()

            # Send welcome email
            send_account_email(
                user,
                temp_password=temp_password,
                role_label="Doctor"
            )

        super().save_model(request, obj, form, change)


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    """Admin interface for creating and managing managers."""
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        """If new manager, generate temp password and send welcome email."""
        if not change:  # Only when creating
            temp_password = get_random_string(8)
            user = obj.user
            user.set_password(temp_password)
            user.role = User.Role.MANAGER
            user.save()

            # Send welcome email
            send_account_email(
                user,
                temp_password=temp_password,
                role_label="Manager"
            )

        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for creating and managing patients."""
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        """If new patient, send confirmation link."""
        if not change:  # New patient
            user = obj.user
            user.role = User.Role.PATIENT
            user.save()

            # Generate confirmation link
            from django.core.signing import Signer
            signer = Signer()
            token = signer.sign(user.email)
            confirm_url = request.build_absolute_uri(
                reverse('accounts:confirm_email', args=[token])
            )

            # Send confirmation email
            send_account_email(
                user,
                confirm_url=confirm_url,
                role_label="Patient"
            )

        super().save_model(request, obj, form, change)
