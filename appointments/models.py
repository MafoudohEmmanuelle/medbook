from django.db import models
from accounts.models import User, Patient, Doctor
from django.utils import timezone

class Planning(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='plannings')
    month = models.PositiveIntegerField()  # 1-12
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('doctor', 'month', 'year')

    def __str__(self):
        return f"{self.doctor} - {self.month}/{self.year}"

    def generate_monthly_slots(self, start_hour=8, end_hour=17, slot_duration=60):
        import calendar
        from datetime import datetime, timedelta, time

        # Clear existing slots for this month
        self.slots.all().delete()

        num_days = calendar.monthrange(self.year, self.month)[1]

        for day in range(1, num_days + 1):
            date_obj = timezone.datetime(self.year, self.month, day).date()
            for hour in range(start_hour, end_hour):
                start_time = datetime.combine(date_obj, time(hour, 0))
                end_time = start_time + timedelta(minutes=slot_duration)
                TimeSlot.objects.create(
                    planning=self,
                    date=date_obj,
                    start_time=start_time.time(),
                    end_time=end_time.time(),
                    status='free'
                )


class TimeSlot(models.Model):
    STATUS_CHOICES = [
        ('free', 'Free'),
        ('reserved', 'Reserved'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
    ]

    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')

    def __str__(self):
        return f"{self.planning.doctor} | {self.date} {self.start_time}-{self.end_time} ({self.status})"


class Beneficiary(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='beneficiaries')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('modified', 'Modified'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = f"{self.beneficiary.first_name} {self.beneficiary.last_name}" if self.beneficiary else self.patient.user.get_full_name()
        return f"{target} -> Dr. {self.doctor.user.last_name} | {self.time_slot.date} {self.time_slot.start_time}"
