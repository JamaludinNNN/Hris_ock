import os
import glob
import re

sidebar_html = """<nav class="flex-1 px-sm space-y-xs">
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'dashboard' %}">
<span class="material-symbols-outlined" data-icon="dashboard">dashboard</span>
<span class="font-body-md text-body-md">Dashboard</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'karyawan' %}">
<span class="material-symbols-outlined" data-icon="groups">groups</span>
<span class="font-body-md text-body-md">Karyawan</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'registrasi' %}">
<span class="material-symbols-outlined" data-icon="face_6">face_6</span>
<span class="font-body-md text-body-md">Registrasi Wajah</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'presensi' %}">
<span class="material-symbols-outlined" data-icon="timer">timer</span>
<span class="font-body-md text-body-md">Presensi</span>
</a>
<a class="flex items-center gap-sm px-md py-sm rounded-lg text-secondary dark:text-secondary-fixed-dim hover:bg-surface-container dark:hover:bg-surface-container-highest transition-colors duration-200 active:scale-95" href="{% url 'laporan' %}">
<span class="material-symbols-outlined" data-icon="assessment">assessment</span>
<span class="font-body-md text-body-md">Laporan</span>
</a>
</nav>"""

for path in glob.glob('templates/**/*.html', recursive=True):
    if 'auth' in path: continue
    
    with open(path, 'r') as f:
        content = f.read()
    
    # We replace <nav> ... </nav> block
    content = re.sub(r'<nav.*?</nav>', sidebar_html, content, flags=re.DOTALL)
    
    with open(path, 'w') as f:
        f.write(content)
