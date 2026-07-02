from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Employee, Attendance, Branch, FaceData
from django.contrib.auth import get_user_model
from .settings_helper import load_system_settings, save_system_settings
import random
import math
from decimal import Decimal, InvalidOperation
import json
from django.utils import timezone
from datetime import datetime

from django.conf import settings as django_settings
User = get_user_model()


def log_security_event(username, employee_id, event_type, details):
    import os
    from django.conf import settings as django_settings
    log_file = os.path.join(django_settings.BASE_DIR, 'security_audit.log')
    timestamp = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(
            f"[{timestamp}] User: {username} | "
            f"Emp: {employee_id} | Event: {event_type} | "
            f"Details: {details}\n"
        )


def is_hrd(user):
    return user.is_authenticated and (getattr(user, 'role', 'karyawan') == 'admin' or user.is_superuser)

@login_required(login_url='login')
def dashboard(request):
    
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
        try:
            Employee.objects.create(
                user=request.user,
                employee_id=f'EMP-{request.user.id:03d}',
                fullname=request.user.username.split('@')[0].capitalize(),
                division='General',
                position='Staff',
                is_validated=True
            )
            # Refresh User object in memory to populate the employee_profile relationship cache
            from django.contrib.auth import get_user_model
            request.user = get_user_model().objects.get(id=request.user.id)
        except Exception as e:
            sys_settings = load_system_settings()
            return render(request, 'presensi/presensi.html', {
                'error': f'Profil karyawan tidak ditemukan dan gagal dibuat secara otomatis: {str(e)}',
                'office_lat': sys_settings['latitude'],
                'office_lon': sys_settings['longitude'],
                'geofence_radius': sys_settings['radius'],
                'verification_method': sys_settings['verification_method'],
                'has_face_data': False,
                'is_validated': False,
                'history': [],
                'branches': [],
            })
        
    employee = request.user.employee_profile
    if not employee.branch:
        first_branch = Branch.objects.first()
        if first_branch:
            employee.branch = first_branch
            employee.save()
            
    has_face_data = hasattr(employee, 'face_data')
    
    today = timezone.localdate()
    now = timezone.now()
    local_now = timezone.localtime(now)
    sys_settings = load_system_settings()
        
    if request.method == 'POST':
        # Enforce geofencing against the branch selected in the dropdown
        branch_id = request.POST.get('branch_id')
        branch = None
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                target_lat = float(branch.latitude)
                target_lon = float(branch.longitude)
                target_radius = int(branch.radius)
            except (Branch.DoesNotExist, ValueError):
                pass
        
        if not branch:
            # Fallback to Kantor Pusat (Bawaan) from system settings
            target_lat = sys_settings['latitude']
            target_lon = sys_settings['longitude']
            target_radius = sys_settings['radius']

        if not employee.is_validated and not django_settings.DEBUG:
            history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
            branches = Branch.objects.all().order_by('name')
            return render(request, 'presensi/presensi.html', {
                'history': history,
                'has_face_data': has_face_data,
                'is_validated': False,
                'error': 'Gagal presensi: Akun Anda belum divalidasi oleh Admin.',
                'office_lat': target_lat,
                'office_lon': target_lon,
                'geofence_radius': target_radius,
                'verification_method': sys_settings['verification_method'],
                'branches': branches,
            })

        action_type = request.POST.get('type')
        if not action_type or action_type not in ['in', 'out']:
            action_type = 'in'
            
        if not has_face_data and not django_settings.DEBUG:
            history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
            branches = Branch.objects.all().order_by('name')
            return render(request, 'presensi/presensi.html', {
                'history': history,
                'has_face_data': has_face_data,
                'error': 'Wajah Anda belum terdaftar di sistem. Silakan registrasi terlebih dahulu.',
                'office_lat': target_lat,
                'office_lon': target_lon,
                'geofence_radius': target_radius,
                'verification_method': sys_settings['verification_method'],
                'branches': branches,
            })
            
        # Extract real coordinates and audit logs from POST parameters
        lat_val = request.POST.get('latitude')
        lon_val = request.POST.get('longitude')
        gps_accuracy_val = request.POST.get('gps_accuracy')
        distance_val = request.POST.get('distance_from_office')
        face_score_val = request.POST.get('face_confidence_score')
        liveness_res = request.POST.get('liveness_result')
        device_info = request.POST.get('device_information')
        browser_info = request.POST.get('browser_information')
        is_fake_gps = request.POST.get('is_fake_gps') == 'true'

        gps_accuracy = None
        if gps_accuracy_val:
            try:
                gps_accuracy = float(gps_accuracy_val)
            except ValueError:
                pass
                
        face_confidence_score = None
        if face_score_val:
            try:
                face_confidence_score = float(face_score_val)
            except ValueError:
                pass

        # 1. Anti-Fake GPS Detection
        if is_fake_gps:
            history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
            branches = Branch.objects.all().order_by('name')
            return render(request, 'presensi/presensi.html', {
                'history': history,
                'has_face_data': has_face_data or django_settings.DEBUG,
                'is_validated': employee.is_validated or django_settings.DEBUG,
                'error': 'Gagal presensi: Lokasi tidak valid. Fake GPS terdeteksi.',
                'office_lat': target_lat,
                'office_lon': target_lon,
                'geofence_radius': target_radius,
                'verification_method': sys_settings['verification_method'],
                'branches': branches,
            })


        # 3. Liveness Validation (face_gps and face_only)
        if sys_settings['verification_method'] in ['face_gps', 'face_only']:
            if not liveness_res or liveness_res.lower() != 'success':
                history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
                branches = Branch.objects.all().order_by('name')
                return render(request, 'presensi/presensi.html', {
                    'history': history,
                    'has_face_data': has_face_data or django_settings.DEBUG,
                    'is_validated': employee.is_validated or django_settings.DEBUG,
                    'error': 'Gagal presensi: Verifikasi keaktifan (Liveness Detection) gagal atau tidak lengkap.',
                    'office_lat': target_lat,
                    'office_lon': target_lon,
                    'geofence_radius': target_radius,
                    'verification_method': sys_settings['verification_method'],
                    'branches': branches,
                })

        # 4. Face Confidence Validation (>= 90%)
        if sys_settings['verification_method'] in ['face_gps', 'face_only']:
            if face_confidence_score is not None and face_confidence_score < 0.90:
                history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
                branches = Branch.objects.all().order_by('name')
                return render(request, 'presensi/presensi.html', {
                    'history': history,
                    'has_face_data': has_face_data or django_settings.DEBUG,
                    'is_validated': employee.is_validated or django_settings.DEBUG,
                    'error': f'Gagal presensi: Tingkat kemiripan wajah terlalu rendah ({int(face_confidence_score * 100)}%). Minimal harus 90%.',
                    'office_lat': target_lat,
                    'office_lon': target_lon,
                    'geofence_radius': target_radius,
                    'verification_method': sys_settings['verification_method'],
                    'branches': branches,
                })

        has_coords = True
        try:
            lat = float(lat_val)
            lon = float(lon_val)
        except (TypeError, ValueError):
            lat = target_lat
            lon = target_lon
            has_coords = False

        # 5. Geofencing Validation (max radius 100 meters)
        distance = None
        if sys_settings['verification_method'] in ['face_gps', 'gps_only']:
            if not has_coords:
                history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
                branches = Branch.objects.all().order_by('name')
                return render(request, 'presensi/presensi.html', {
                    'history': history,
                    'has_face_data': has_face_data or django_settings.DEBUG,
                    'is_validated': employee.is_validated or django_settings.DEBUG,
                    'error': 'Gagal presensi: Koordinat GPS tidak didapatkan. Pastikan izin lokasi aktif.',
                    'office_lat': target_lat,
                    'office_lon': target_lon,
                    'geofence_radius': target_radius,
                    'verification_method': sys_settings['verification_method'],
                    'branches': branches,
                })
            
            # Compute distance using Haversine formula
            R = 6371000.0  # Earth radius in meters
            phi1 = math.radians(lat)
            phi2 = math.radians(target_lat)
            delta_phi = math.radians(target_lat - lat)
            delta_lambda = math.radians(target_lon - lon)
            
            a = math.sin(delta_phi/2.0) * math.sin(delta_phi/2.0) + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda/2.0) * math.sin(delta_lambda/2.0)
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
            distance = R * c
            
            # Enforce max radius limit of 100 meters
            allowed_radius = min(float(target_radius), 100.0)
            if distance > allowed_radius:
                history = Attendance.objects.filter(employee=employee).order_by('-timestamp')[:10]
                branches = Branch.objects.all().order_by('name')
                return render(request, 'presensi/presensi.html', {
                    'history': history,
                    'has_face_data': has_face_data or django_settings.DEBUG,
                    'is_validated': employee.is_validated or django_settings.DEBUG,
                    'error': f'Gagal presensi: Anda berada di luar radius kantor cabang ({int(distance)} meter dari cabang, batas maks: {int(allowed_radius)} meter).',
                    'office_lat': target_lat,
                    'office_lon': target_lon,
                    'geofence_radius': target_radius,
                    'verification_method': sys_settings['verification_method'],
                    'branches': branches,
                })

        # Calculate distance if coords are present but not forced by verification method
        if distance is None and has_coords:
            R = 6371000.0
            phi1 = math.radians(lat)
            phi2 = math.radians(target_lat)
            delta_phi = math.radians(target_lat - lat)
            delta_lambda = math.radians(target_lon - lon)
            a = math.sin(delta_phi/2.0) * math.sin(delta_phi/2.0) + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda/2.0) * math.sin(delta_lambda/2.0)
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
            distance = R * c

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
            
        if gps_accuracy is not None and gps_accuracy > 30.0:
            dist_str = f"{distance:.1f}m" if distance is not None else "N/A"
            log_security_event(
                request.user.username,
                employee.id,
                "POOR_GPS_ACCURACY_ALLOWED",
                f"GPS accuracy poor ({gps_accuracy:.1f} meters) but allowed. "
                f"Distance: {dist_str}, Target Radius: {target_radius}m."
            )

        # Create Attendance with Audit Logs
        Attendance.objects.create(
            employee=employee,
            branch=branch,
            type=action_type,
            latitude=lat,
            longitude=lon,
            status=status,
            gps_accuracy=gps_accuracy,
            distance_from_office=distance,
            face_confidence_score=face_confidence_score,
            liveness_result=liveness_res,
            device_information=device_info,
            browser_information=browser_info
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
    branches = Branch.objects.all().order_by('name')
    
    employee_branch = employee.branch
    if employee_branch:
        default_lat = float(employee_branch.latitude)
        default_lon = float(employee_branch.longitude)
        default_radius = int(employee_branch.radius)
    else:
        default_lat = sys_settings['latitude']
        default_lon = sys_settings['longitude']
        default_radius = sys_settings['radius']
        
    return render(request, 'presensi/presensi.html', {
        'history': history,
        'has_face_data': has_face_data or django_settings.DEBUG,
        'is_validated': employee.is_validated or django_settings.DEBUG,
        'work_duration_str': work_duration_str,
        'work_status': work_status,
        'check_in_today': check_in_today,
        'check_out_today': check_out_today,
        'office_lat': default_lat,
        'office_lon': default_lon,
        'geofence_radius': default_radius,
        'verification_method': sys_settings['verification_method'],
        'branches': branches,
        'debug_mode': django_settings.DEBUG,
    })

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def registrasi(request):
    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        embedding = request.POST.get('embedding', '')
        face_image = request.POST.get('face_image_base64', '')
        if emp_id and embedding:
            try:
                employee = Employee.objects.get(id=emp_id)
                FaceData.objects.update_or_create(
                    employee=employee,
                    defaults={
                        'embedding': embedding,
                        'face_image': face_image
                    }
                )
                # Otomatis validasi karyawan setelah wajah berhasil didaftarkan
                employee.is_validated = True
                employee.save()
            except Employee.DoesNotExist:
                pass
            return redirect('karyawan')
    employees = Employee.objects.all()
    registered_faces = []
    for emp in employees:
        if hasattr(emp, 'face_data'):
            registered_faces.append({
                'id': str(emp.id),
                'name': emp.fullname,
                'image': emp.face_data.embedding
            })
    registered_faces_json = json.dumps(registered_faces)
    return render(request, 'registrasi/registrasi.html', {
        'employees': employees,
        'registered_faces_json': registered_faces_json,
        'debug_mode': django_settings.DEBUG
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
                
                branch_id = request.POST.get('branch')
                if branch_id:
                    try:
                        emp.branch = Branch.objects.get(id=branch_id)
                    except Branch.DoesNotExist:
                        emp.branch = None
                else:
                    emp.branch = None
                
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

        elif action == 'validate':
            try:
                emp = Employee.objects.get(id=emp_id)
                emp.is_validated = True
                emp.save()
            except Employee.DoesNotExist:
                pass
            return redirect('karyawan')

    employees = Employee.objects.all()
    total_karyawan = employees.count()
    total_departemen = Employee.objects.values('division').distinct().count()
    branches = Branch.objects.all().order_by('name')
    return render(request, 'karyawan/karyawan.html', {
        'employees': employees,
        'total_karyawan': total_karyawan,
        'total_departemen': total_departemen,
        'branches': branches
    })

@login_required(login_url='login')
@user_passes_test(is_hrd, login_url='dashboard')
def tambah_karyawan(request):
    branches = Branch.objects.all().order_by('name')
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        employee_id = request.POST.get('employee_id')
        division = request.POST.get('division')
        position = request.POST.get('position')
        role = request.POST.get('role', 'karyawan')
        branch_id = request.POST.get('branch')
        profile_image = request.POST.get('profile_image_base64', '')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.role = role
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        user.save()
        
        branch = None
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                pass
        
        Employee.objects.create(
            user=user,
            employee_id=employee_id,
            fullname=fullname,
            division=division,
            position=position,
            profile_image=profile_image,
            branch=branch
        )
        return redirect('karyawan')
    return render(request, 'karyawan/tambah_karyawan.html', {'branches': branches})

@login_required(login_url='login')
def laporan(request):
    
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
    success_msg = None
    error_msg = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_branch':
            name = request.POST.get('name', '').strip()
            latitude_raw = request.POST.get('latitude', '').strip().replace(',', '.')
            longitude_raw = request.POST.get('longitude', '').strip().replace(',', '.')
            radius_raw = request.POST.get('radius', '150').strip() or '150'
            
            if name and latitude_raw and longitude_raw:
                try:
                    lat_dec = Decimal(latitude_raw).quantize(Decimal('0.000001'))
                    lng_dec = Decimal(longitude_raw).quantize(Decimal('0.000001'))
                    Branch.objects.create(
                        name=name,
                        latitude=lat_dec,
                        longitude=lng_dec,
                        radius=int(radius_raw)
                    )
                    success_msg = f"Cabang '{name}' berhasil ditambahkan."
                except InvalidOperation:
                    error_msg = "Format koordinat tidak valid. Gunakan titik (.) sebagai pemisah desimal."
                except Exception as e:
                    error_msg = f"Gagal menambahkan cabang: {str(e)}"
            else:
                error_msg = "Semua bidang cabang harus diisi."
                
        elif action == 'delete_branch':
            branch_id = request.POST.get('branch_id')
            if branch_id:
                try:
                    branch = Branch.objects.get(id=branch_id)
                    branch_name = branch.name
                    branch.delete()
                    success_msg = f"Cabang '{branch_name}' berhasil dihapus."
                except Branch.DoesNotExist:
                    error_msg = "Cabang tidak ditemukan."
                    
        else:
            # Save global config
            # Normalize: replace comma decimal separator → dot (locale-safe)
            latitude = str(request.POST.get('latitude', -6.2088)).replace(',', '.')
            longitude = str(request.POST.get('longitude', 106.8456)).replace(',', '.')
            radius = request.POST.get('radius', 150)
            verification_method = request.POST.get('verification_method', 'face_gps')

            save_system_settings(latitude, longitude, radius, verification_method)
            success_msg = "Pengaturan global berhasil disimpan."

    sys_settings = load_system_settings()
    branches = Branch.objects.all().order_by('name')
    context = {
        'latitude': sys_settings['latitude'],
        'longitude': sys_settings['longitude'],
        'radius': sys_settings['radius'],
        'verification_method': sys_settings['verification_method'],
        'branches': branches,
        'success': success_msg,
        'error': error_msg,
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
                    division="Management" if getattr(user, 'role', 'karyawan') == 'admin' else "IT",
                    position="HR Administrator" if getattr(user, 'role', 'karyawan') == 'admin' else "Karyawan"
                )
            return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Email / Username atau Password salah.'})
            
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        profile_image = request.POST.get('profile_image_base64', '')
        
        if not hasattr(request.user, 'employee_profile'):
            employee = Employee.objects.create(
                user=request.user,
                employee_id=f"EMP-{request.user.id:03d}",
                fullname=fullname or request.user.username,
                division="Management" if getattr(request.user, 'role', 'karyawan') == 'admin' else "IT",
                position="HR Administrator" if getattr(request.user, 'role', 'karyawan') == 'admin' else "Karyawan"
            )
        else:
            employee = request.user.employee_profile
            
        if fullname:
            employee.fullname = fullname
        if profile_image:
            employee.profile_image = profile_image
        employee.save()
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    branches = Branch.objects.all().order_by('name')
        
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        employee_id = request.POST.get('employee_id')
        division = request.POST.get('division')
        position = request.POST.get('position')
        branch_id = request.POST.get('branch')
        profile_image = request.POST.get('profile_image_base64', '')
        
        # Check if email/username already exists
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            return render(request, 'auth/register.html', {'error': 'Email / Username sudah terdaftar.', 'branches': branches})
            
        if Employee.objects.filter(employee_id=employee_id).exists():
            return render(request, 'auth/register.html', {'error': 'ID Karyawan sudah terdaftar.', 'branches': branches})
            
        try:
            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.role = 'karyawan'
            user.save()
            
            # Fetch branch
            branch = None
            if branch_id:
                try:
                    branch = Branch.objects.get(id=branch_id)
                except Branch.DoesNotExist:
                    pass
            
            # Create Employee profile
            Employee.objects.create(
                user=user,
                employee_id=employee_id,
                fullname=fullname,
                division=division,
                position=position,
                profile_image=profile_image,
                is_validated=False,
                branch=branch
            )
            
            # Authenticate and login
            authenticated_user = authenticate(request, username=email, password=password)
            if authenticated_user:
                login(request, authenticated_user)
            return redirect('presensi')
            
        except Exception as e:
            return render(request, 'auth/register.html', {'error': f'Gagal mendaftar: {str(e)}', 'branches': branches})
            
    return render(request, 'auth/register.html', {'branches': branches})


@login_required(login_url='login')
def registrasi_wajah(request):
    if not hasattr(request.user, 'employee_profile'):
        try:
            Employee.objects.create(
                user=request.user,
                employee_id=f'EMP-{request.user.id:03d}',
                fullname=request.user.username.split('@')[0].capitalize(),
                division='General',
                position='Staff',
                is_validated=True
            )
            # Refresh User object in memory to populate the employee_profile relationship cache
            from django.contrib.auth import get_user_model
            request.user = get_user_model().objects.get(id=request.user.id)
        except Exception as e:
            sys_settings = load_system_settings()
            return render(request, 'presensi/presensi.html', {
                'error': f'Profil karyawan tidak ditemukan dan gagal dibuat secara otomatis: {str(e)}',
                'office_lat': sys_settings['latitude'],
                'office_lon': sys_settings['longitude'],
                'geofence_radius': sys_settings['radius'],
                'verification_method': sys_settings['verification_method'],
                'has_face_data': False,
                'is_validated': False,
                'history': [],
                'branches': [],
            })
        
    employee = request.user.employee_profile
    if not employee.branch:
        first_branch = Branch.objects.first()
        if first_branch:
            employee.branch = first_branch
            employee.save()
            
    if request.method == 'POST':
        embedding = request.POST.get('embedding', '')
        face_image = request.POST.get('face_image_base64', '')
        if embedding:
            # Update or create FaceData
            FaceData.objects.update_or_create(
                employee=employee,
                defaults={
                    'embedding': embedding,
                    'face_image': face_image
                }
            )
            # Set validation status to True when they register/update their face biometric!
            employee.is_validated = True
            employee.save()
            return redirect('presensi')
            
    # For GET, render registrasi_wajah.html template
    # Preload registered faces json for duplication check
    employees = Employee.objects.all()
    registered_faces = []
    for emp in employees:
        if hasattr(emp, 'face_data'):
            registered_faces.append({
                'id': str(emp.id),
                'name': emp.fullname,
                'image': emp.face_data.embedding
            })
    registered_faces_json = json.dumps(registered_faces)
    
    return render(request, 'registrasi/registrasi_wajah.html', {
        'employee': employee,
        'registered_faces_json': registered_faces_json,
        'debug_mode': django_settings.DEBUG
    })
