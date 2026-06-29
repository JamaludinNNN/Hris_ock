from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('karyawan', 'Karyawan'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='karyawan'
    )


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True
    )
    employee_id = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=150)
    division = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    profile_image = models.TextField(null=True, blank=True)
    is_validated = models.BooleanField(default=False)
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    def __str__(self):
        return f"{self.employee_id} - {self.fullname}"


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius = models.IntegerField(default=150)

    def __str__(self):
        return self.name


class FaceData(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='face_data'
    )
    embedding = models.TextField()
    face_image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('on_time', 'On Time'),
        ('late', 'Late'),
    )
    TYPE_CHOICES = (
        ('in', 'Clock In'),
        ('out', 'Clock Out'),
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='in'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Security Audit Logs
    gps_accuracy = models.FloatField(null=True, blank=True)
    distance_from_office = models.FloatField(null=True, blank=True)
    face_confidence_score = models.FloatField(null=True, blank=True)
    liveness_result = models.CharField(max_length=50, null=True, blank=True)
    device_information = models.TextField(null=True, blank=True)
    browser_information = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.fullname} - {self.type} - {self.timestamp}"
