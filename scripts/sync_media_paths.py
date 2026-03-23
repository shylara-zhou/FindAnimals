import os
import sys
from pathlib import Path

import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, 'FindAnimals')
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FindAnimals.settings')
django.setup()

from animalsdata.models import Animal, Park
from django.db.models import Q


def list_existing_images():
    media_root = Path(settings.MEDIA_ROOT)
    img_dir = media_root / 'img'
    files = {}
    if img_dir.exists():
        for p in img_dir.iterdir():
            if p.is_file():
                files[p.name.lower()] = str(p.relative_to(media_root)).replace('\\', '/')
    return files


NAME_KEYS = {
    'panda': 'panda.jpg',
    'lion': 'lion.jpg',
    'tiger': 'tiger.jpg',
    '熊猫': 'panda.jpg',
    '狮': 'lion.jpg',
    '狮子': 'lion.jpg',
    '虎': 'tiger.jpg',
    '老虎': 'tiger.jpg',
}


def choose_by_name(name: str, existing: dict):
    low = (name or '').lower()
    for key, fname in NAME_KEYS.items():
        if key in low and fname.lower() in existing:
            return existing[fname.lower()]
    return None


def sync_animals(existing):
    media_root = Path(settings.MEDIA_ROOT)
    qs = Animal.objects.all().order_by('-created_at')
    updated = 0
    for a in qs:
        cur = a.photo.name if a.photo else ''
        target = None
        if cur:
            file_path = media_root / cur
            if file_path.exists():
                continue  # ok
        # try by name
        target = choose_by_name(a.name, existing)
        if not target and 'default_animal.jpg' in existing:
            target = existing['default_animal.jpg']
        if target:
            a.photo.name = target
            a.save(update_fields=['photo'])
            updated += 1
            print(f'Animal {a.id} -> {a.photo.name}')
    print(f'Animals updated: {updated}')


def sync_parks(existing):
    media_root = Path(settings.MEDIA_ROOT)
    qs = Park.objects.all().order_by('-created_at')
    updated = 0
    for p in qs:
        cur = p.cover.name if p.cover else ''
        if cur:
            path = media_root / cur
            if path.exists():
                continue
        # Use top-viewed approved animal photo as cover if available
        top = p.animals.filter(audit_status='approved', photo__isnull=False).order_by('-views_count').first()
        if top and top.photo:
            p.cover.name = top.photo.name
            p.save(update_fields=['cover'])
            updated += 1
            print(f'Park {p.id} cover -> {p.cover.name} (from animal {top.id})')
            continue
        # else fallback default
        if 'default_animal.jpg' in existing:
            p.cover.name = existing['default_animal.jpg']
            p.save(update_fields=['cover'])
            updated += 1
            print(f'Park {p.id} cover -> {p.cover.name} (default)')
    print(f'Parks updated: {updated}')


def main():
    existing = list_existing_images()
    print(f'Found {len(existing)} files under media/img: {list(existing.keys())}')
    sync_animals(existing)
    sync_parks(existing)


if __name__ == '__main__':
    main()