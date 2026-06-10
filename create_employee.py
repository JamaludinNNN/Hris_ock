import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hris_ock.settings")
django.setup()

from presensi.models import Employee, User
user = User.objects.get(username='admin')
if not Employee.objects.filter(user=user).exists():
    Employee.objects.create(
        user=user,
        employee_id='EMP-001',
        fullname='Administrator',
        division='IT',
        position='System Admin'
    )
    print("Employee profile created for admin.")
