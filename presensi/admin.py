from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Employee, Branch, FaceData, Attendance, Schedule


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Configuration', {'fields': ('role',)}),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'fullname', 'division', 'position', 'branch', 'face_status', 'face_verified')
    list_filter = ('face_status', 'face_verified', 'division', 'branch')
    search_fields = ('employee_id', 'fullname', 'division', 'position', 'user__username', 'user__email')
    raw_id_fields = ('user',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius')
    search_fields = ('name',)


@admin.register(FaceData)
class FaceDataAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at')
    search_fields = ('employee__fullname', 'employee__employee_id')
    raw_id_fields = ('employee',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'status', 'branch', 'timestamp', 'gps_accuracy', 'distance_from_office', 'face_confidence_score')
    list_filter = ('type', 'status', 'branch', 'timestamp')
    search_fields = ('employee__fullname', 'employee__employee_id')
    raw_id_fields = ('employee', 'branch')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'shift_name', 'is_off', 'start_time', 'end_time', 'start_date', 'end_date', 'created_at')
    list_filter = ('is_off', 'shift_name', 'date', 'start_date')
    search_fields = ('employee__fullname', 'employee__employee_id', 'shift_name')
    raw_id_fields = ('employee',)
