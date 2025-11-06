from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import User, Doctor, Patient, Manager
from .forms import CustomUserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
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
        if not change:
            # Do not set password here; first login triggers setup
            obj.set_unusable_password()
            obj.save()
        else:
            super().save_model(request, obj, form, change)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'years_of_experience')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        if not change:
            # Assign role and mark password as unusable
            user = obj.user
            user.role = User.Role.DOCTOR
            user.set_unusable_password()
            user.save()
        super().save_model(request, obj, form, change)


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        if not change:
            # Assign role and mark password as unusable
            user = obj.user
            user.role = User.Role.MANAGER
            user.is_staff = True
            user.set_unusable_password()
            user.save()
        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def save_model(self, request, obj, form, change):
        if not change:
            # Assign role to patient
            user = obj.user
            user.role = User.Role.PATIENT
            user.save()
        super().save_model(request, obj, form, change)
