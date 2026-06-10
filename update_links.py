import os
import glob

def update_file(path):
    with open(path, 'r') as f:
        content = f.read()

    # Dashboard
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-sm">dashboard</span>\n<span class="font-body-md">Dashboard</span>', 'href="{% url \'dashboard\' %}">\n<span class="material-symbols-outlined mr-sm">dashboard</span>\n<span class="font-body-md">Dashboard</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined group-hover:text-primary">dashboard</span>\n<span class="font-body-md">Dashboard</span>', 'href="{% url \'dashboard\' %}">\n<span class="material-symbols-outlined group-hover:text-primary">dashboard</span>\n<span class="font-body-md">Dashboard</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-md">dashboard</span>\n<span class="font-body-md">Dashboard</span>', 'href="{% url \'dashboard\' %}">\n<span class="material-symbols-outlined mr-md">dashboard</span>\n<span class="font-body-md">Dashboard</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined" data-icon="dashboard">dashboard</span>\n<span class="font-body-md text-body-md">Dashboard</span>', 'href="{% url \'dashboard\' %}">\n<span class="material-symbols-outlined" data-icon="dashboard">dashboard</span>\n<span class="font-body-md text-body-md">Dashboard</span>')

    # Registrasi Wajah
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-sm">face_6</span>\n<span class="font-body-md">Registrasi Wajah</span>', 'href="{% url \'registrasi\' %}">\n<span class="material-symbols-outlined mr-sm">face_6</span>\n<span class="font-body-md">Registrasi Wajah</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-md">face_6</span>\n<span class="font-body-md">Registrasi Wajah</span>', 'href="{% url \'registrasi\' %}">\n<span class="material-symbols-outlined mr-md">face_6</span>\n<span class="font-body-md">Registrasi Wajah</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined group-hover:text-primary">face</span>\n<span class="font-body-md">Face Registration</span>', 'href="{% url \'registrasi\' %}">\n<span class="material-symbols-outlined group-hover:text-primary">face</span>\n<span class="font-body-md">Face Registration</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined" data-icon="face_6">face_6</span>\n<span class="font-body-md text-body-md">Registrasi Wajah</span>', 'href="{% url \'registrasi\' %}">\n<span class="material-symbols-outlined" data-icon="face_6">face_6</span>\n<span class="font-body-md text-body-md">Registrasi Wajah</span>')

    # Presensi
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-sm">timer</span>\n<span class="font-body-md">Presensi</span>', 'href="{% url \'presensi\' %}">\n<span class="material-symbols-outlined mr-sm">timer</span>\n<span class="font-body-md">Presensi</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-md">timer</span>\n<span class="font-body-md">Presensi</span>', 'href="{% url \'presensi\' %}">\n<span class="material-symbols-outlined mr-md">timer</span>\n<span class="font-body-md">Presensi</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined group-hover:text-primary">location_on</span>\n<span class="font-body-md">Presence</span>', 'href="{% url \'presensi\' %}">\n<span class="material-symbols-outlined group-hover:text-primary">location_on</span>\n<span class="font-body-md">Presence</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined" data-icon="timer">timer</span>\n<span class="font-body-md text-body-md">Presensi</span>', 'href="{% url \'presensi\' %}">\n<span class="material-symbols-outlined" data-icon="timer">timer</span>\n<span class="font-body-md text-body-md">Presensi</span>')

    # Logout
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-sm">logout</span>', 'href="{% url \'login\' %}">\n<span class="material-symbols-outlined mr-sm">logout</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined mr-md">logout</span>', 'href="{% url \'login\' %}">\n<span class="material-symbols-outlined mr-md">logout</span>')
    content = content.replace('href="#">\n<span class="material-symbols-outlined" data-icon="logout">logout</span>', 'href="{% url \'login\' %}">\n<span class="material-symbols-outlined" data-icon="logout">logout</span>')

    # Form action in login
    content = content.replace('action="#"', 'action="{% url \'dashboard\' %}"')

    with open(path, 'w') as f:
        f.write(content)

for file in glob.glob('templates/**/*.html', recursive=True):
    update_file(file)

