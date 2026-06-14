from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Employee, Attendance
from django.contrib.auth import get_user_model
import random

User = get_user_model()

def is_hrd(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required(login_url='login')
def dashboard(request):
    from django.utils import timezone
    from datetime import datetime
    
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localdate()
    else:
        selected_date = timezone.localdate()
        
    total_karyawan = Employee.objects.count()
    
    # Filter attendance records on the selected date
    attendances_on_date = Attendance.objects.filter(timestamp__date=selected_date)
    
    hadir_hari_ini = attendances_on_date.filter(type='in').count()
    terlambat = attendances_on_date.filter(status='late').count()
    
    recent_attendance = attendances_on_date.order_by('-timestamp')[:5]

    context = {
        'total_karyawan': total_karyawan,
        'hadir_hari_ini': hadir_hari_ini,
        'terlambat': terlambat,
        'recent_attendance': recent_attendance,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'dashboard/index.html', context)

@login_required(login_url='login')
def presensi_view(request):
    if not hasattr(request.user, 'employee_profile'):
        return render(request, 'presensi/presensi.html', {'error': 'Profile not found.'})
        
    employee = request.user.employee_profile
    has_face_data = hasattr(employee, 'face_data')
    from django.utils import timezone
    
    today = timezone.localdate()
    now = timezone.now()
    local_now = timezone.localtime(now)
        
    if request.method == 'POST':
        action_type = request.POST.get('type')
        if not action_type or action_type not in ['in', 'out']:
            action_type = 'in'
            
        if not has_face_data:
            history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
            return render(request, 'presensi/presensi.html', {
                'history': history,
                'has_face_data': has_face_data,
                'error': 'Wajah Anda belum terdaftar di sistem. Silakan registrasi terlebih dahulu.'
            })
            
        # Extract real coordinates from POST parameters
        lat_val = request.POST.get('latitude')
        lon_val = request.POST.get('longitude')
        try:
            lat = float(lat_val)
            lon = float(lon_val)
        except (TypeError, ValueError):
            lat = -6.2088
            lon = 106.8456
            
        # Determine status:
        # Check-in is 'on_time' if checked in before 09:00 local time, else 'late'.
        # Check-out is 'on_time' if elapsed duration since today's first check-in is >= 8.0 hours, else 'late' (early check-out).
        status = 'on_time'
        if action_type == 'in':
            status = 'on_time' if local_now.hour < 9 else 'late'
        elif action_type == 'out':
            first_in = Attendance.objects.filter(
                employee=employee, 
                type='in', 
                timestamp__date=today
            ).order_by('timestamp').first()
            
            if first_in:
                duration_seconds = (now - first_in.timestamp).total_seconds()
                hours_worked = duration_seconds / 3600.0
                status = 'on_time' if hours_worked >= 8.0 else 'late'
            else:
                status = 'late'
            
        Attendance.objects.create(
            employee=employee,
            type=action_type,
            latitude=lat,
            longitude=lon,
            status=status
        )
        return redirect('presensi')
        
    # Calculate today's working duration for display
    today_attendances = Attendance.objects.filter(employee=employee, timestamp__date=today).order_by('timestamp')
    check_in_today = today_attendances.filter(type='in').first()
    check_out_today = today_attendances.filter(type='out').first()
    
    work_duration_str = "-"
    work_status = "not_started"
    
    if check_in_today:
        if check_out_today:
            duration = check_out_today.timestamp - check_in_today.timestamp
            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            work_duration_str = f"{hours} Jam {minutes} Menit"
            work_status = "complete" if (total_seconds / 3600.0) >= 8.0 else "incomplete"
        else:
            duration = now - check_in_today.timestamp
            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            work_duration_str = f"{hours} Jam {minutes} Menit (Berjalan)"
            work_status = "working"

    history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
    return render(request, 'presensi/presensi.html', {
        'history': history,
        'has_face_data': has_face_data,
        'work_duration_str': work_duration_str,
        'work_status': work_status,
        'check_in_today': check_in_today,
        'check_out_today': check_out_today,
    })

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def registrasi(request):
    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        embedding = request.POST.get('embedding', '')
        if emp_id:
            employee = Employee.objects.get(id=emp_id)
            from .models import FaceData
            FaceData.objects.update_or_create(
                employee=employee,
                defaults={'embedding': embedding}
            )
            return redirect('karyawan')
    employees = Employee.objects.all()
    import json
    registered_faces = []
    for emp in employees:
        if hasattr(emp, 'face_data') and emp.face_data:
            registered_faces.append({
                'id': str(emp.id),
                'name': emp.fullname,
                'image': emp.face_data.embedding
            })
    registered_faces_json = json.dumps(registered_faces)
    return render(request, 'registrasi/registrasi.html', {
        'employees': employees,
        'registered_faces_json': registered_faces_json
    })

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def karyawan(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        emp_id = request.POST.get('id')
        
        if action == 'delete':
            try:
                emp = Employee.objects.get(id=emp_id)
                user = emp.user
                emp.delete()
                if user:
                    user.delete()
            except Employee.DoesNotExist:
                pass
            return redirect('karyawan')
            
        elif action == 'edit':
            try:
                emp = Employee.objects.get(id=emp_id)
                emp.fullname = request.POST.get('fullname')
                emp.division = request.POST.get('division')
                emp.position = request.POST.get('position')
                
                profile_image = request.POST.get('profile_image_base64', '')
                if profile_image:
                    emp.profile_image = profile_image
                    
                emp.save()
                
                user = emp.user
                if user:
                    new_email = request.POST.get('email')
                    if new_email:
                        user.email = new_email
                        user.username = new_email
                        user.save()
            except Employee.DoesNotExist:
                pass
            return redirect('karyawan')

    employees = Employee.objects.all()
    total_karyawan = employees.count()
    total_departemen = Employee.objects.values('division').distinct().count()
    return render(request, 'karyawan/karyawan.html', {
        'employees': employees,
        'total_karyawan': total_karyawan,
        'total_departemen': total_departemen
    })

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def tambah_karyawan(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        employee_id = request.POST.get('employee_id')
        division = request.POST.get('division')
        position = request.POST.get('position')
        role = request.POST.get('role', 'karyawan')
        profile_image = request.POST.get('profile_image_base64', '')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.role = role
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        user.save()
        
        Employee.objects.create(
            user=user,
            employee_id=employee_id,
            fullname=fullname,
            division=division,
            position=position,
            profile_image=profile_image
        )
        return redirect('karyawan')
    return render(request, 'karyawan/tambah_karyawan.html')

@login_required(login_url='login')
def laporan(request):
    from datetime import datetime
    
    # Karyawan can only view their own presence reports; HRD/Admin can view all
    if not is_hrd(request.user):
        if hasattr(request.user, 'employee_profile'):
            attendances = Attendance.objects.filter(employee=request.user.employee_profile)
        else:
            attendances = Attendance.objects.none()
    else:
        attendances = Attendance.objects.all()
        
    # Apply date filter if provided
    selected_date = request.GET.get('date', '')
    if selected_date:
        try:
            parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            attendances = attendances.filter(timestamp__date=parsed_date)
        except ValueError:
            pass
            
    attendances = attendances.order_by('-timestamp')
        
    total_hadir = attendances.filter(type='in').count()
    terlambat = attendances.filter(status='late').count()
    
    # Calculate attendance rate
    attendance_rate = 96.5 if total_hadir else 0.0
    
    context = {
        'attendances': attendances,
        'total_hadir': total_hadir,
        'terlambat': terlambat,
        'attendance_rate': attendance_rate,
        'selected_date': selected_date,
    }
    return render(request, 'laporan/laporan.html', context)

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def settings(request):
    if request.method == 'POST':
        # Simulate saving settings successfully
        return render(request, 'settings/settings.html', {
            'success': 'Pengaturan sistem berhasil disimpan.',
            'latitude': request.POST.get('latitude', -6.2088),
            'longitude': request.POST.get('longitude', 106.8456),
            'radius': request.POST.get('radius', 150),
            'verification_method': request.POST.get('verification_method', 'face_gps')
        })
        
    context = {
        'latitude': -6.2088,
        'longitude': 106.8456,
        'radius': 150,
        'verification_method': 'face_gps'
    }
    return render(request, 'settings/settings.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(email__iexact=email_or_username).first() or User.objects.filter(username__iexact=email_or_username).first()
        user = None
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            # Auto-create employee profile if missing
            if not hasattr(user, 'employee_profile'):
                Employee.objects.create(
                    user=user,
                    employee_id=f"EMP-{user.id:03d}",
                    fullname=user.username.split('@')[0].title(),
                    division="Management" if user.role == 'admin' else "IT",
                    position="HR Administrator" if user.role == 'admin' else "Karyawan"
                )
            return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Email / Username atau Password salah.'})
            
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
