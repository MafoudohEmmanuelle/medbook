from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from accounts.models import User, Patient, Doctor, Manager
from django.contrib.auth import get_user_model

User = get_user_model()

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'})
    )
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'})
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[("Male", "Male"), ("Female", "Female")],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'gender',
            'phone',
            'address',
            'date_of_birth',
            'email',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth')
            )
        return user
    
class DoctorRegistrationForm(forms.ModelForm):
    """Used by admin to create a doctor account with minimal info."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        user.set_unusable_password()  # ⬅️ mark password as not yet set
        if commit:
            user.save()
            Doctor.objects.create(user=user)
        return user

class DoctorProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = Doctor
        fields = ['specialty', 'years_of_experience', 'biography']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['address'].initial = self.instance.user.address
            self.fields['profile_image'].initial = self.instance.user.profile_image

    def save(self, commit=True):
        doctor = super().save(commit=False)
        user = doctor.user
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data.get('profile_image')
        if commit:
            user.save()
            doctor.save()
        return doctor

class ManagerCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.MANAGER
        user.is_staff = True
        user.set_unusable_password()
        if commit:
            user.save()
            Manager.objects.create(user=user)
        return user

class ManagerProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = Manager
        fields = []  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['address'].initial = self.instance.user.address
            self.fields['profile_image'].initial = self.instance.user.profile_image

    def save(self, commit=True):
        manager = super().save(commit=False)
        user = manager.user
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data.get('profile_image')
        if commit:
            user.save()
            manager.save()
        return manager

class EmailOnlyLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class DefinePasswordForm(SetPasswordForm):
    """Form for users to define their password for the first time."""
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']


class CustomUserCreationForm(forms.ModelForm):
    """Form to create a user without requiring password in admin."""

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name','role')