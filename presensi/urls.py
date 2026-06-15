from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('presensi/', views.presensi_view, name='presensi'),
    path('registrasi/', views.registrasi, name='registrasi'),
    path('karyawan/', views.karyawan, name='karyawan'),
    path('karyawan/tambah/', views.tambah_karyawan, name='tambah_karyawan'),
    path('laporan/', views.laporan, name='laporan'),
    path('settings/', views.settings, name='settings'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
