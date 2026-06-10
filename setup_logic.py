import os
import re
import shutil

os.makedirs('templates/karyawan', exist_ok=True)
shutil.copy('templates/karyawan/karyawan.html', 'templates/karyawan/tambah_karyawan.html')

with open('templates/karyawan/tambah_karyawan.html', 'r') as f:
    content = f.read()

form_html = """
<div class="bg-surface-container-lowest p-lg rounded-xl shadow-sm border border-outline-variant max-w-2xl">
    <h3 class="font-headline-md text-headline-md text-on-surface mb-md">Form Tambah Karyawan</h3>
    <form method="POST" action="{% url 'tambah_karyawan' %}" class="space-y-md">
        {% csrf_token %}
        <div>
            <label class="block font-label-md text-on-surface-variant mb-xs">Nama Lengkap</label>
            <input type="text" name="fullname" required class="w-full px-md py-sm rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface-container-lowest text-on-surface">
        </div>
        <div>
            <label class="block font-label-md text-on-surface-variant mb-xs">Email</label>
            <input type="email" name="email" required class="w-full px-md py-sm rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface-container-lowest text-on-surface">
        </div>
        <div>
            <label class="block font-label-md text-on-surface-variant mb-xs">ID Karyawan</label>
            <input type="text" name="employee_id" required class="w-full px-md py-sm rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface-container-lowest text-on-surface">
        </div>
        <div class="grid grid-cols-2 gap-md">
            <div>
                <label class="block font-label-md text-on-surface-variant mb-xs">Departemen</label>
                <input type="text" name="division" required class="w-full px-md py-sm rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface-container-lowest text-on-surface">
            </div>
            <div>
                <label class="block font-label-md text-on-surface-variant mb-xs">Jabatan</label>
                <input type="text" name="position" required class="w-full px-md py-sm rounded-lg border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary outline-none bg-surface-container-lowest text-on-surface">
            </div>
        </div>
        <div class="pt-md flex gap-sm justify-end">
            <a href="{% url 'karyawan' %}" class="px-xl py-sm border border-outline text-secondary rounded-lg font-label-md hover:bg-surface-container transition-all">Batal</a>
            <button type="submit" class="px-xl py-sm bg-primary text-on-primary rounded-lg font-label-md shadow-sm hover:bg-primary-container transition-all">Simpan Karyawan</button>
        </div>
    </form>
</div>
"""

grid_start = content.find('<!-- Filters and Stats Bento Grid -->')
main_end = content.find('</main>')
if grid_start != -1 and main_end != -1:
    content = content[:grid_start] + form_html + "\n" + content[main_end:]

content = content.replace('Manajemen Data Karyawan', 'Tambah Karyawan Baru')
content = content.replace('Kelola informasi profil, departemen, dan status aktif karyawan.', 'Masukkan data karyawan baru ke dalam sistem.')
content = re.sub(r'<button class="bg-primary text-on-primary.*?Tambah Karyawan Baru\s*</button>', '', content, flags=re.DOTALL)

with open('templates/karyawan/tambah_karyawan.html', 'w') as f:
    f.write(content)

# Now update karyawan.html to change button to a tag
with open('templates/karyawan/karyawan.html', 'r') as f:
    karyawan_content = f.read()

karyawan_content = re.sub(
    r'<button class="bg-primary text-on-primary px-6 py-3 rounded-xl font-label-md flex items-center gap-2 shadow-lg hover:bg-primary-container transition-all active:scale-95">\s*<span class="material-symbols-outlined">person_add</span>\s*Tambah Karyawan Baru\s*</button>',
    '<a href="{% url \'tambah_karyawan\' %}" class="bg-primary text-on-primary px-6 py-3 rounded-xl font-label-md flex items-center gap-2 shadow-lg hover:bg-primary-container transition-all active:scale-95"><span class="material-symbols-outlined">person_add</span> Tambah Karyawan Baru</a>',
    karyawan_content
)

with open('templates/karyawan/karyawan.html', 'w') as f:
    f.write(karyawan_content)
