from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import User, Patient, Doctor, Manager

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    address = forms.CharField(required=False)
    phone = forms.CharField(required=True)
    gender = forms.ChoiceField(
        required=False,
        choices=[("Male", "Male"), ("Female", "Female")]
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

        #  Generate and assign random password
        temp_password = User.objects.make_random_password()
        user.set_password(temp_password)

        if commit:
            user.save()
            Doctor.objects.create(user=user)

        # Return both for email sending
        return user, temp_password

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

        temp_password = User.objects.make_random_password()
        user.set_password(temp_password)
        user.is_staff = True  # Optional for admin panel access

        if commit:
            user.save()
            Manager.objects.create(user=user)

        return user, temp_password

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

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
