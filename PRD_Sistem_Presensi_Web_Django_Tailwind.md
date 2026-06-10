# Product Requirements Document (PRD)

## Sistem Presensi Karyawan Berbasis Web dengan Face Recognition & GPS Geofencing

### 1. Ringkasan Produk

Sistem presensi karyawan berbasis web yang memungkinkan proses absensi
menggunakan verifikasi wajah (face recognition) dan validasi lokasi (GPS
geofencing). Sistem dirancang responsive agar dapat digunakan pada
desktop maupun smartphone.

### 2. Tujuan Produk

-   Mengurangi manipulasi absensi
-   Mempermudah monitoring kehadiran karyawan
-   Menyediakan dashboard real-time untuk admin
-   Memastikan presensi hanya dapat dilakukan di area valid

------------------------------------------------------------------------

# 3. Target User

## Admin HR / Administrator

-   Mengelola data karyawan
-   Monitoring kehadiran
-   Melihat laporan presensi
-   Mengelola biometrik wajah

## Karyawan

-   Login sistem
-   Registrasi wajah
-   Melakukan presensi
-   Melihat riwayat presensi

------------------------------------------------------------------------

# 4. Technology Stack

## Backend

-   Framework: Django
-   API: Django REST Framework
-   Authentication: Django Authentication + JWT / Session

## Frontend

-   Template Engine: Django Templates
-   Styling: Tailwind CSS
-   Icons: Heroicons / Lucide
-   Charts: Chart.js

## Database

-   PostgreSQL

## Storage

-   Media Storage untuk data wajah

## Deployment

-   Nginx
-   Gunicorn
-   Ubuntu Server

------------------------------------------------------------------------

# 5. Modul Sistem

## 5.1 Login Pengguna

### Objective

Memberikan autentikasi pengguna.

### Features

-   Login email / username
-   Password
-   Remember me
-   Logout
-   Session management

### UI Components

-   Form login
-   Illustration panel
-   Button login
-   Error validation

------------------------------------------------------------------------

## 5.2 Dashboard Admin

### Objective

Monitoring sistem secara real-time.

### Components

### KPI Cards

-   Total karyawan
-   Total presensi
-   Keterlambatan
-   Kehadiran hari ini

### Charts

-   Grafik presensi
-   Statistik bulanan

### Tables

-   Aktivitas terbaru
-   Presensi terbaru

------------------------------------------------------------------------

## 5.3 Manajemen Data Karyawan

### Features

-   CRUD karyawan
-   Search
-   Pagination
-   Filter departemen
-   Upload foto

### Table Fields

  Field     Type
  --------- -----------------
  Nama      Text
  Email     Text
  Jabatan   Text
  Divisi    Text
  Status    Active/Inactive

------------------------------------------------------------------------

## 5.4 Registrasi Wajah

### Objective

Mendaftarkan biometrik pengguna.

### Features

-   Akses kamera
-   Capture wajah
-   Multiple scan
-   Preview hasil scan
-   Validasi kualitas wajah

### Flow

1.  User membuka halaman registrasi
2.  Kamera aktif
3.  Sistem capture beberapa frame
4.  Embedding wajah disimpan

------------------------------------------------------------------------

## 5.5 Portal Presensi

### Features

-   Kamera aktif
-   Face verification
-   GPS validation
-   Status validasi
-   Tombol presensi

### Flow

1.  User membuka portal
2.  Kamera aktif
3.  Lokasi diperiksa
4.  Wajah diverifikasi
5.  Presensi berhasil

------------------------------------------------------------------------

# 6. Functional Requirements

## Authentication

-   User dapat login
-   User dapat logout
-   Session timeout

## Employee Management

-   Admin CRUD karyawan
-   Admin search/filter data

## Face Recognition

-   Registrasi wajah
-   Verifikasi wajah

## GPS Geofencing

-   Validasi radius lokasi
-   Menolak lokasi di luar area

## Attendance

-   Check in
-   Check out
-   History

------------------------------------------------------------------------

# 7. Non Functional Requirements

## Performance

-   Response \< 3 detik
-   Support 100+ concurrent users

## Security

-   CSRF Protection
-   Password hashing
-   Permission based access

## Responsiveness

-   Desktop
-   Tablet
-   Mobile

------------------------------------------------------------------------

# 8. Database Draft

## Users

-   id
-   username
-   password
-   role

## Employees

-   employee_id
-   fullname
-   division
-   position

## Face Data

-   employee
-   embedding
-   created_at

## Attendance

-   employee
-   timestamp
-   latitude
-   longitude
-   status

------------------------------------------------------------------------

# 9. Django Project Structure

``` text
attendance_system/

├── accounts/
├── employees/
├── attendance/
├── face_recognition/
├── dashboard/
├── templates/
├── static/
├── media/
├── config/
└── manage.py
```

------------------------------------------------------------------------

# 10. Tailwind Structure

``` text
templates/

base.html

components/

sidebar.html
navbar.html
card.html
table.html
modal.html

pages/

dashboard.html
employees.html
attendance.html
login.html
```

------------------------------------------------------------------------

# 11. UI Guidelines

Colors:

-   Primary Blue
-   White
-   Gray

Style:

-   Clean
-   Modern
-   Minimal

Components:

-   Rounded cards
-   Soft shadows
-   Large spacing
-   Mobile responsive

------------------------------------------------------------------------

# 12. Future Scope

-   Mobile App
-   Push Notification
-   Payroll Integration
-   Multi Branch Support
