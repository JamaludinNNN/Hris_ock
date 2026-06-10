import os
import glob
import re

# 1. Fix presensi.html buttons
with open('templates/presensi/presensi.html', 'r') as f:
    content = f.read()

buttons_html = """<form method="POST" action="{% url 'presensi' %}" class="mt-md flex gap-md w-full">
    {% csrf_token %}
    <button type="submit" name="type" value="in" class="flex-[1] bg-surface-container text-on-surface font-headline-md py-lg rounded-xl shadow hover:-translate-y-1 transition-all active:scale-95 flex items-center justify-center gap-md">
        <span class="material-symbols-outlined text-[32px]">login</span>
        Presensi Masuk
    </button>
    <button type="submit" name="type" value="out" class="flex-[1.5] bg-primary text-on-primary font-headline-md py-lg rounded-xl shadow-lg hover:shadow-primary/30 hover:-translate-y-1 transition-all active:scale-95 flex items-center justify-center gap-md">
        <span class="material-symbols-outlined text-[32px]">logout</span>
        Presensi Keluar
    </button>
</form>"""

# Find the buttons block
# It starts with <div class="mt-md flex gap-md">
content = re.sub(r'<div class="mt-md flex gap-md">.*?</div>', buttons_html, content, flags=re.DOTALL)

with open('templates/presensi/presensi.html', 'w') as f:
    f.write(content)

# 2. Update sidebars across all templates
sidebar_replacement = """<nav class="flex-1 px-sm space-y-xs">
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'dashboard' %}">
<span class="material-symbols-outlined" data-icon="dashboard">dashboard</span>
<span class="font-body-md text-body-md">Dashboard</span>
</a>
{% if request.user.role == 'admin' or request.user.is_superuser %}
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'karyawan' %}">
<span class="material-symbols-outlined" data-icon="groups">groups</span>
<span class="font-body-md text-body-md">Karyawan</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'registrasi' %}">
<span class="material-symbols-outlined" data-icon="face_6">face_6</span>
<span class="font-body-md text-body-md">Registrasi Wajah</span>
</a>
{% endif %}
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'presensi' %}">
<span class="material-symbols-outlined" data-icon="timer">timer</span>
<span class="font-body-md text-body-md">Presensi</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'laporan' %}">
<span class="material-symbols-outlined" data-icon="assessment">assessment</span>
<span class="font-body-md text-body-md">Laporan</span>
</a>
</nav>"""

settings_replacement = """{% if request.user.role == 'admin' or request.user.is_superuser %}
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary hover:bg-surface-container transition-colors active:scale-95" href="{% url 'settings' %}">
<span class="material-symbols-outlined" data-icon="settings">settings</span>
<span class="font-body-md text-body-md">Settings</span>
</a>
{% endif %}
"""

for path in glob.glob('templates/**/*.html', recursive=True):
    if 'auth' in path: continue
    with open(path, 'r') as f:
        html = f.read()
    
    html = re.sub(r'<nav class="flex-1 px-sm space-y-xs">.*?</nav>', sidebar_replacement, html, flags=re.DOTALL)
    
    # Also restrict settings link
    html = re.sub(r'<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary hover:bg-surface-container transition-colors active:scale-95" href="{% url \'settings\' %}">\s*<span class="material-symbols-outlined" data-icon="settings">settings</span>\s*<span class="font-body-md text-body-md">Settings</span>\s*</a>', settings_replacement, html, flags=re.DOTALL)

    # In views, replace header user to show correct logged in user
    html = re.sub(r'<p class="text-label-md font-bold text-on-surface">Admin User</p>', '<p class="text-label-md font-bold text-on-surface">{{ request.user.employee_profile.fullname }}</p>', html)
    html = re.sub(r'<p class="text-\[10px\] text-on-surface-variant uppercase tracking-wider">Super Admin</p>', '<p class="text-[10px] text-on-surface-variant uppercase tracking-wider">{{ request.user.employee_profile.position }}</p>', html)

    with open(path, 'w') as f:
        f.write(html)

