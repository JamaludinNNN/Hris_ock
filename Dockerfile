# Gunakan image resmi Python yang ringan
FROM python:3.12-slim

# Atur environment variables
# Mencegah Python menulis file .pyc ke disk
ENV PYTHONDONTWRITEBYTECODE=1
# Mencegah Python menyangga (buffering) stdout dan stderr
ENV PYTHONUNBUFFERED=1

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Instal dependensi sistem yang mungkin dibutuhkan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements.txt dan instal dependensi Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek ke dalam direktori kerja
COPY . /app/

# Kumpulkan file statis (static files) untuk production
RUN python manage.py collectstatic --noinput

# Informasikan port yang digunakan (Railway akan memetakan ini secara otomatis via env PORT)
EXPOSE 8000

# Jalankan migrasi database, buat admin & profil karyawan, lalu jalankan server Gunicorn saat container dimulai
CMD ["sh", "-c", "python manage.py migrate --noinput && python create_admin.py && python create_employee.py && gunicorn hris_ock.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
