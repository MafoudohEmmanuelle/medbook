from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Planning, TimeSlot, Appointment, Beneficiary, DoctorUnavailability
from .forms import GlobalPlanningForm, DoctorUnavailabilityForm, BeneficiaryForm
from accounts.models import Doctor, Patient

# --- Manager: create planning for a doctor ---
@login_required
def create_planning(request):
    if not hasattr(request.user, "manager"):
        messages.error(request, "Only managers can create planning.")
        return redirect("core:home")

    if request.method == "POST":
        form = GlobalPlanningForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data["month"]
            year = form.cleaned_data["year"]
            start_hour = form.cleaned_data["start_hour"]
            end_hour = form.cleaned_data["end_hour"]
            slot_duration = form.cleaned_data["slot_duration"]

            # Generate planning for all doctors
            doctors = Doctor.objects.all()
            for doctor in doctors:
                planning, _ = Planning.objects.get_or_create(doctor=doctor, month=month, year=year)
                planning.generate_monthly_slots(
                    start_hour=start_hour,
                    end_hour=end_hour,
                    slot_duration=slot_duration
                )
            messages.success(request, f"Planning created for all doctors for {month}/{year}")
            return redirect("core:manager_dashboard")
    else:
        form = GlobalPlanningForm()
    return render(request, "appointment/create_planning.html", {"form": form})

# --- Manager/Doctor: mark unavailability ---
@login_required
def mark_unavailability(request):
    user = request.user
    if hasattr(user, "doctor"):
        doctor = user.doctor
    elif hasattr(user, "manager"):
        doctor = None  # manager can select doctor in the form
    else:
        messages.error(request, "You are not authorized.")
        return redirect("core:home")

    if request.method == "POST":
        form = DoctorUnavailabilityForm(request.POST, user=user)
        if form.is_valid():
            unavailability = form.save()
            unavailability.block_slots()
            messages.success(request, "Doctor unavailability marked and slots blocked.")
            return redirect("core:manager_dashboard" if hasattr(user, "manager") else "core:doctor_dashboard")
    else:
        form = DoctorUnavailabilityForm(user=user)
    return render(request, "appointment/mark_unavailability.html", {"form": form})

# --- Patient: view doctor slots ---
@login_required
def view_doctor_slots(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slots = TimeSlot.objects.filter(
        planning__doctor=doctor, status="free", date__gte=timezone.now().date()
    ).order_by("date", "start_time")
    return render(request, "appointment/view_slots.html", {"doctor": doctor, "slots": slots})

# --- Patient: book appointment ---
@login_required
def book_appointment(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id, status="free")
    patient = request.user.patient

    if request.method == "POST":
        # Determine if booking for self or another person
        if request.POST.get("for_self"):
            beneficiary = None
        else:
            form = BeneficiaryForm(request.POST)
            if form.is_valid():
                beneficiary = form.save(commit=False)
                beneficiary.patient = patient
                beneficiary.save()
            else:
                return render(request, "appointment/book_appointment.html", {"slot": slot, "form": form})

        Appointment.objects.create(
            patient=patient,
            doctor=slot.planning.doctor,
            time_slot=slot,
            beneficiary=beneficiary
        )
        slot.status = "reserved"
        slot.save()
        messages.success(request, "Appointment booked successfully.")
        return redirect("core:patient_dashboard")
    else:
        form = BeneficiaryForm()
    return render(request, "appointment/book_appointment.html", {"slot": slot, "form": form})

# --- Doctor: manage appointments ---
@login_required
def manage_appointments(request):
    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor, time_slot__date__gte=timezone.now().date()).order_by("time_slot__date", "time_slot__start_time")
    return render(request, "appointment/manage_appointments.html", {"appointments": appointments})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    appointment.time_slot.status = "free"
    appointment.time_slot.save()
    appointment.delete()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect("appointment:manage_appointments")

@login_required
def mark_done(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    appointment.status = "completed"
    appointment.save()
    messages.success(request, "Appointment marked as done.")
    return redirect("appointment:manage_appointments")
