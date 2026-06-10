import os
import re
import glob
import shutil

# First, create laporan.html and settings.html by copying dashboard/index.html
os.makedirs('templates/laporan', exist_ok=True)
os.makedirs('templates/settings', exist_ok=True)

if not os.path.exists('templates/laporan/laporan.html'):
    shutil.copy('templates/dashboard/index.html', 'templates/laporan/laporan.html')
if not os.path.exists('templates/settings/settings.html'):
    shutil.copy('templates/dashboard/index.html', 'templates/settings/settings.html')

# We need a standard sidebar block
sidebar_html = """
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
"""

for path in glob.glob('templates/**/*.html', recursive=True):
    if 'auth' in path: continue
    
    with open(path, 'r') as f:
        content = f.read()
    
    # Simple fix for Settings and Laporan URLs anywhere
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined\"[^>]*>settings</span>', 'href=\"{% url \'settings\' %}\">\n<span class=\"material-symbols-outlined\" data-icon=\"settings\">settings</span>', content)
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined mr-sm\">settings</span>', 'href=\"{% url \'settings\' %}\">\n<span class=\"material-symbols-outlined mr-sm\">settings</span>', content)
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined mr-md\">settings</span>', 'href=\"{% url \'settings\' %}\">\n<span class=\"material-symbols-outlined mr-md\">settings</span>', content)
    
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined\"[^>]*>assessment</span>', 'href=\"{% url \'laporan\' %}\">\n<span class=\"material-symbols-outlined\" data-icon=\"assessment\">assessment</span>', content)
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined mr-sm\">assessment</span>', 'href=\"{% url \'laporan\' %}\">\n<span class=\"material-symbols-outlined mr-sm\">assessment</span>', content)
    content = re.sub(r'href=\"#\"[^>]*>\s*<span class=\"material-symbols-outlined mr-md\">assessment</span>', 'href=\"{% url \'laporan\' %}\">\n<span class=\"material-symbols-outlined mr-md\">assessment</span>', content)

    # For registrasi.html Camera
    if 'registrasi.html' in path:
        # Replace the img tag with a video tag
        img_tag_regex = r'<img alt=\"Camera context\".*?>'
        content = re.sub(img_tag_regex, '<video id="camera-stream" autoplay playsinline class="w-full h-full object-cover transform scale-x-[-1]"></video>', content)
        
        # Add JS to start camera
        js_code = """
        <script>
            async function startCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    const videoEl = document.getElementById('camera-stream');
                    videoEl.srcObject = stream;
                } catch (err) {
                    console.error("Error accessing camera: ", err);
                    alert("Tidak dapat mengakses kamera. Pastikan izin kamera diberikan.");
                }
            }
            document.addEventListener('DOMContentLoaded', startCamera);
        """
        content = content.replace('<script>', js_code, 1)

    # For presensi.html Camera
    if 'presensi.html' in path:
        img_tag_regex = r'<img alt=\"Live Webcam Feed\".*?>'
        content = re.sub(img_tag_regex, '<video id="camera-stream" autoplay playsinline class="w-full h-full object-cover transform scale-x-[-1]"></video>', content)
        
        js_code = """
        <script>
            async function startCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    const videoEl = document.getElementById('camera-stream');
                    videoEl.srcObject = stream;
                } catch (err) {
                    console.error("Error accessing camera: ", err);
                    alert("Tidak dapat mengakses kamera. Pastikan izin kamera diberikan.");
                }
            }
            document.addEventListener('DOMContentLoaded', startCamera);
        """
        content = content.replace('<script>', js_code, 1)

    # For Laporan and Settings, let's just clear the main content and put a placeholder if it's the duplicated ones
    if 'laporan.html' in path:
        content = re.sub(r'<!-- Headline Section -->.*?(?=</main>)', '<!-- Headline Section --><div class="p-lg"><h2 class="text-headline-lg font-headline-lg">Laporan Presensi</h2><p class="text-body-md text-secondary">Halaman laporan sedang dalam pengembangan.</p></div>', content, flags=re.DOTALL)
    
    if 'settings.html' in path:
        content = re.sub(r'<!-- Headline Section -->.*?(?=</main>)', '<!-- Headline Section --><div class="p-lg"><h2 class="text-headline-lg font-headline-lg">Pengaturan Sistem</h2><p class="text-body-md text-secondary">Halaman pengaturan sedang dalam pengembangan.</p></div>', content, flags=re.DOTALL)


    with open(path, 'w') as f:
        f.write(content)

