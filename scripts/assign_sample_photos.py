import os
import sys
import random

import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ensure the inner Django project package is importable
PROJECT_DIR = os.path.join(BASE_DIR, 'FindAnimals')
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FindAnimals.settings')
django.setup()

from animalsdata.models import Animal
from django.db.models import Q

SAMPLE_FILES = [
    'img/panda.jpg',
    'img/lion.jpg',
    'img/tiger.jpg',
    'img/elephant.jpg',
    'img/giraffe.jpg',
    'img/zebra.jpg',
    # always have a fallback
    'img/default_animal.jpg',
]

NAME_TO_FILE = {
    'panda': 'img/panda.jpg',
    'lion': 'img/lion.jpg',
    'tiger': 'img/tiger.jpg',
    'elephant': 'img/elephant.jpg',
    'giraffe': 'img/giraffe.jpg',
    'zebra': 'img/zebra.jpg',
    # Chinese keywords
    '熊猫': 'img/panda.jpg',
    '狮': 'img/lion.jpg',
    '狮子': 'img/lion.jpg',
    '虎': 'img/tiger.jpg',
    '老虎': 'img/tiger.jpg',
}

def assign_sample_photos():
    # Narrow down to files that actually exist to avoid broken links
    media_root = os.path.join(settings.BASE_DIR.parent, 'media')
    existing_files = []
    for f in SAMPLE_FILES:
        if os.path.exists(os.path.join(media_root, f)):
            existing_files.append(f)
    if not existing_files:
        existing_files = ['img/default_animal.jpg']
    qs = Animal.objects.filter(Q(photo__isnull=True) | Q(photo='')).order_by('-created_at')
    count = qs.count()
    print(f'Animals without photo: {count}')
    for idx, animal in enumerate(qs):
        # Try deterministic mapping by name keywords
        name_lower = (animal.name or '').lower()
        filename = None
        for key, file in NAME_TO_FILE.items():
            if key in name_lower and os.path.exists(os.path.join(media_root, file)):
                filename = file
                break
        if not filename:
            filename = random.choice(existing_files)
        # Assign by setting the file name relative to storage root
        animal.photo.name = filename
        animal.save(update_fields=['photo'])
        print(f'Assigned {filename} to animal {animal.id} ({animal.name})')

if __name__ == '__main__':
    assign_sample_photos()