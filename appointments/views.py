from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
from .models import Planning, TimeSlot, Appointment, DoctorUnavailability
from accounts.models import Doctor, Patient
from .forms import GlobalPlanningForm, DoctorUnavailabilityForm, BeneficiaryForm
from django.utils import timezone
from calendar import monthrange


# === Utility check functions ===

def is_manager(user):
    return hasattr(user, "manager")

def is_doctor(user):
    return hasattr(user, "doctor")

def is_patient(user):
    return hasattr(user, "patient")


# === MANAGER: Global planning generation ===

@login_required
@user_passes_test(is_manager)
def generate_global_planning(request):
    """
    Manager defines the global planning for doctors,
    marks unavailable periods, and generates valid slots.
    """
    doctors = Doctor.objects.all().order_by("user__last_name")

    if request.method == "POST":
        form = GlobalPlanningForm(request.POST)
        selected_doctors = request.POST.getlist("doctors")

        if form.is_valid():
            month = form.cleaned_data["month"]
            year = form.cleaned_data["year"]
            start_hour = form.cleaned_data["start_hour"]
            end_hour = form.cleaned_data["end_hour"]
            slot_duration = form.cleaned_data["slot_duration"]

            for doctor_id in selected_doctors:
                doctor = Doctor.objects.get(id=doctor_id)
                planning, _ = Planning.objects.get_or_create(
                    doctor=doctor, month=month, year=year
                )

                # Remove existing slots
                planning.slots.all().delete()

                from datetime import datetime, time
                import calendar
                num_days = calendar.monthrange(year, month)[1]
                unavailabilities = DoctorUnavailability.objects.filter(doctor=doctor)

                for day in range(1, num_days + 1):
                    date_obj = timezone.datetime(year, month, day).date()

                    # Skip unavailable days
                    if any(ua.start_date <= date_obj <= ua.end_date for ua in unavailabilities):
                        continue

                    for hour in range(start_hour, end_hour):
                        start_time = datetime.combine(date_obj, time(hour, 0))
                        end_time = start_time + timedelta(minutes=slot_duration)
                        TimeSlot.objects.create(
                            planning=planning,
                            date=date_obj,
                            start_time=start_time.time(),
                            end_time=end_time.time(),
                            status="free",
                        )

            messages.success(request, "Global planning generated successfully.")
            return redirect("appointments:generate_global_planning")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = GlobalPlanningForm()

    unavailability_form = DoctorUnavailabilityForm()
    context = {
        "form": form,
        "doctors": doctors,
        "unavailability_form": unavailability_form,
    }
    return render(request, "appointments/generate_global_planning.html", context)


# === MANAGER/DOCTOR: Add unavailability ===

@login_required
def add_doctor_unavailability(request):
    """
    Allows managers or doctors to define unavailable date ranges.
    """
    if request.method == "POST":
        form = DoctorUnavailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Unavailability period saved successfully.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    return redirect("appointments:generate_global_planning")


# === PATIENT: View available slots and book ===

@login_required
@user_passes_test(is_patient)
def view_doctor_schedule(request, doctor_id):
    """
    Display a doctor’s available slots for booking.
    """
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slots = TimeSlot.objects.filter(planning__doctor=doctor, status="free").order_by("date", "start_time")
    return render(request, "appointments/view_doctor_schedule.html", {"doctor": doctor, "slots": slots})


@login_required
@user_passes_test(is_patient)
def book_appointment(request, doctor_id, slot_id):
    """
    Patient books an appointment with a doctor and a specific time slot.
    """
    patient = get_object_or_404(Patient, user=request.user)
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slot = get_object_or_404(TimeSlot, id=slot_id, status="free")

    if request.method == "POST":
        book_for_someone = request.POST.get("for_someone") == "true"
        beneficiary = None

        if book_for_someone:
            form = BeneficiaryForm(request.POST)
            if form.is_valid():
                beneficiary = form.save(commit=False)
                beneficiary.patient = patient
                beneficiary.save()
            else:
                messages.error(request, "Please complete beneficiary information.")
                return redirect(request.path)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            time_slot=slot,
            beneficiary=beneficiary,
            status="confirmed"
        )
        slot.status = "reserved"
        slot.save()

        messages.success(request, "Appointment booked successfully.")
        return redirect("appointments:my_appointments")

    form = BeneficiaryForm()
    return render(request, "appointments/book_appointment.html", {
        "doctor": doctor,
        "slot": slot,
        "form": form
    })


# === PATIENT: View their appointments ===

@login_required
@user_passes_test(is_patient)
def my_appointments(request):
    """
    Display all appointments for the logged-in patient.
    """
    patient = get_object_or_404(Patient, user=request.user)
    appointments = patient.appointments.select_related("doctor", "time_slot").order_by("-created_at")
    return render(request, "appointments/my_appointments.html", {"appointments": appointments})


# === DOCTOR: Manage appointments ===

@login_required
@user_passes_test(is_doctor)
def doctor_appointments(request):
    """
    Display all appointments for the logged-in doctor.
    """
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = doctor.appointments.select_related("patient", "time_slot").order_by("time_slot__date", "time_slot__start_time")
    return render(request, "appointments/doctor_appointments.html", {"appointments": appointments})


@login_required
@user_passes_test(is_doctor)
def update_appointment_status(request, appointment_id, action):
    """
    Doctor can confirm, cancel, or mark appointment as done.
    """
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    valid_actions = {
        "confirm": "confirmed",
        "cancel": "cancelled",
        "done": "completed",
    }

    if action not in valid_actions:
        messages.error(request, "Invalid action.")
        return redirect("appointments:doctor_appointments")

    appointment.status = valid_actions[action]
    appointment.save()

    # Free slot if appointment is cancelled
    if action == "cancel":
        appointment.time_slot.status = "free"
        appointment.time_slot.save()

    messages.success(request, f"Appointment {action} successfully.")
    return redirect("appointments:doctor_appointments")

@login_required
@user_passes_test(is_manager)
def manager_planning(request):
    """
    Display current month planning for all doctors.
    If no planning exists for the month, show a button to generate it.
    """
    today = timezone.now().date()
    month = today.month
    year = today.year

    # Retrieve all plannings for the current month
    plannings = Planning.objects.filter(month=month, year=year).prefetch_related('slots', 'doctor')
    
    if plannings.exists():
        # Pass the first planning for simplicity (you can customize per doctor)
        planning = plannings.first()
    else:
        planning = None

    context = {
        "planning": planning,
        "month": month,
        "year": year,
    }
    return render(request, "appointments/manager_planning.html", context)

@login_required
@user_passes_test(is_manager)
def block_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    slot.status = "blocked"
    slot.save()
    messages.success(request, "Slot blocked successfully.")
    return redirect("appointments:manager_planning")


@login_required
@user_passes_test(is_manager)
def unblock_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    slot.status = "free"
    slot.save()
    messages.success(request, "Slot unblocked successfully.")
    return redirect("appointments:manager_planning")
