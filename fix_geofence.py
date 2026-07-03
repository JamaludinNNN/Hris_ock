import re

with open('templates/presensi/presensi.html', 'r') as f:
    content = f.read()

# 1. line 580-582
content = re.sub(
    r'gpsGeofenceStatus\.innerText = isKantorPusat \? \'Bebas Geofencing\' : \'Mengunci GPS...\';\s*gpsGeofenceStatus\.className = `font-label-md font-bold \$\{isKantorPusat \? \'text-tertiary\' : \'text-outline animate-pulse\'\}`;\s*liveDistanceDetails\.innerText = isKantorPusat\s*\? \'Kantor Pusat \(Bebas Geofencing\)\'\s*: \'Mendeteksi koordinat lokasi presensi Anda...\';',
    "gpsGeofenceStatus.innerText = 'Mengunci GPS...';\ngpsGeofenceStatus.className = 'font-label-md font-bold text-outline animate-pulse';\nliveDistanceDetails.innerText = 'Mendeteksi koordinat lokasi presensi Anda...';",
    content
)

# 2. line 718
content = re.sub(
    r'if \(VERIFICATION_METHOD === \'face_only\' \|\| isKantorPusat\) \{',
    "if (VERIFICATION_METHOD === 'face_only') {",
    content
)

# 3. line 928-931
content = re.sub(
    r'gpsGeofenceStatus\.innerText = isKantorPusat \? \'Bebas Geofencing\' : \'Mengunci GPS...\';\s*gpsGeofenceStatus\.className = `font-label-md font-bold \$\{isKantorPusat \? \'text-tertiary\' : \'text-outline animate-pulse\'\}`;\s*liveDistanceDetails\.innerText = isKantorPusat\s*\? \'Kantor Pusat \(Bebas Geofencing\)\'\s*: \'Mendeteksi koordinat lokasi presensi Anda...\';',
    "gpsGeofenceStatus.innerText = 'Mengunci GPS...';\ngpsGeofenceStatus.className = 'font-label-md font-bold text-outline animate-pulse';\nliveDistanceDetails.innerText = 'Mendeteksi koordinat lokasi presensi Anda...';",
    content
)

# 4. line 942-943
content = re.sub(
    r'gpsGeofenceStatus\.innerText = isKantorPusat \? \'Bebas Geofencing\' : \'GPS Tidak Tersedia\';\s*gpsGeofenceStatus\.className = `font-label-md font-bold \$\{isKantorPusat \? \'text-tertiary\' : \'text-amber-500\'\}`;',
    "gpsGeofenceStatus.innerText = 'GPS Tidak Tersedia';\ngpsGeofenceStatus.className = 'font-label-md font-bold text-amber-500';",
    content
)

# 5. line 947
content = re.sub(
    r'if \(!isKantorPusat\) fallbackToIPGeolocation\(\'Browser no geolocation support\'\);',
    "fallbackToIPGeolocation('Browser no geolocation support');",
    content
)

# 6. line 989-990
content = re.sub(
    r'gpsGeofenceStatus\.innerText = isKantorPusat \? \'Bebas Geofencing\' : \'GPS Ditolak\';\s*gpsGeofenceStatus\.className = `font-label-md font-bold \$\{isKantorPusat \? \'text-tertiary\' : \'text-error\'\}`;',
    "gpsGeofenceStatus.innerText = 'GPS Ditolak';\ngpsGeofenceStatus.className = 'font-label-md font-bold text-error';",
    content
)

# 7. line 994
content = re.sub(
    r'if \(!isKantorPusat\) fallbackToIPGeolocation\(`Permission denied`\);',
    "fallbackToIPGeolocation(`Permission denied`);",
    content
)

# 8. line 997
content = re.sub(
    r'if \(!isKantorPusat\) fallbackToIPGeolocation\(`GPS error: \$\{errType\} - \$\{err\.message\}`\);',
    "fallbackToIPGeolocation(`GPS error: ${errType} - ${err.message}`);",
    content
)

# 9. line 1530
content = re.sub(
    r'if \(!isKantorPusat && \(VERIFICATION_METHOD === \'face_gps\' \|\| VERIFICATION_METHOD === \'gps_only\'\)\) \{',
    "if (VERIFICATION_METHOD === 'face_gps' || VERIFICATION_METHOD === 'gps_only') {",
    content
)

with open('templates/presensi/presensi.html', 'w') as f:
    f.write(content)
