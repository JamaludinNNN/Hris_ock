import os
import json
from django.conf import settings as django_settings

SETTINGS_FILE = os.path.join(django_settings.BASE_DIR, 'system_settings.json')

DEFAULT_SETTINGS = {
    'latitude': -6.2088,
    'longitude': 106.8456,
    'radius': 150,
    'verification_method': 'face_gps'
}


def load_system_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
            # Ensure all keys are present
            settings_dict = DEFAULT_SETTINGS.copy()
            settings_dict.update(data)
            # Cast type correctly
            settings_dict['latitude'] = float(settings_dict['latitude'])
            settings_dict['longitude'] = float(settings_dict['longitude'])
            settings_dict['radius'] = int(settings_dict['radius'])
            return settings_dict
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_system_settings(latitude, longitude, radius, verification_method):
    try:
        data = {
            'latitude': float(latitude),
            'longitude': float(longitude),
            'radius': int(radius),
            'verification_method': str(verification_method)
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False
