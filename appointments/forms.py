from django import forms
from .models import Beneficiary, DoctorUnavailability
from django.utils.translation import gettext_lazy as _
from datetime import date
from accounts.models import Doctor

class GlobalPlanningForm(forms.Form):
    month = forms.IntegerField(
        min_value=1,
        max_value=12,
        label="Month",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        min_value=2024,
        max_value=2100,
        label="Year",
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    start_hour = forms.IntegerField(
        min_value=0,
        max_value=23,
        initial=8,
        label="Start Hour",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    end_hour = forms.IntegerField(
        min_value=0,
        max_value=23,
        initial=17,
        label="End Hour",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    slot_duration = forms.IntegerField(
        min_value=15,
        max_value=240,
        initial=60,
        label="Slot Duration (minutes)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class DoctorUnavailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorUnavailability
        fields = ["doctor", "start_date", "end_date", "reason"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "reason": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional reason"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Hide doctor field for logged-in doctors (not for managers)
        if user and hasattr(user, "doctor"):
            self.fields["doctor"].widget = forms.HiddenInput()
            self.fields["doctor"].initial = user.doctor

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and start > end:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['first_name', 'last_name', 'gender', 'age']
        labels = {
            'first_name': _("First Name"),
            'last_name': _("Last Name"),
            'gender': _("Gender"),
            'age': _("Age"),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter first name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter last name')
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': _('Enter age')
            }),
        }

