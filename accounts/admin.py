from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.signing import Signer

from .models import User, Doctor, Patient, Manager
from .utils import send_account_email
from .forms import CustomUserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm  # <- use custom form
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'address', 'profile_image', 'gender', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )

    def save_model(self, request, obj, form, change):
        """Automatically generate password and send email when creating new user."""
        if not change:
            temp_password = get_random_string(8)
            obj.set_password(temp_password)
            obj.save()

            # Send welcome email
            send_account_email(
                obj,
                temp_password=temp_password,
                role_label=obj.get_role_display()
            )
        else:
            super().save_model(request, obj, form, change)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin interface for doctors."""
    list_display = ('user', 'specialty', 'years_of_experience')
    search_fields = ('user_email', 'userfirst_name', 'user_last_name')

    def save_model(self, request, obj, form, change):
        """Generate password for doctor and send email."""
        if not change:
            temp_password = get_random_string(8)
            user = obj.user
            user.set_password(temp_password)
            user.role = User.Role.DOCTOR
            user.save()

            send_account_email(
                user,
                temp_password=temp_password,
                role_label="Doctor"
            )
        super().save_model(request, obj, form, change)


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    """Admin interface for managers."""
    list_display = ('user',)
    search_fields = ('user_email', 'userfirst_name', 'user_last_name')

    def save_model(self, request, obj, form, change):
        """Generate password for manager and send email."""
        if not change:
            temp_password = get_random_string(8)
            user = obj.user
            user.set_password(temp_password)
            user.role = User.Role.MANAGER
            user.save()

            send_account_email(
                user,
                temp_password=temp_password,
                role_label="Manager"
            )
        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for patients."""
    list_display = ('user', 'date_of_birth')
    search_fields = ('user_email', 'userfirst_name', 'user_last_name')

    def save_model(self, request, obj, form, change):
        """Send confirmation email for new patient."""
        if not change:
            user = obj.user
            user.role = User.Role.PATIENT
            user.save()

            signer = Signer()
            token = signer.sign(user.email)
            confirm_url = request.build_absolute_uri(
                reverse('accounts:confirm_email', args=[token])
            )

            send_account_email(
                user,
                confirm_url=confirm_url,
                role_label="Patient"
            )
        super().save_model(request, obj, form, change)