import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_IMG_DIR = os.path.join(BASE_DIR, 'media', 'img')

COPIES = [
    'panda.jpg',
    'lion.jpg',
    'tiger.jpg',
]

def main():
    src = os.path.join(MEDIA_IMG_DIR, 'default_animal.jpg')
    if not os.path.exists(src):
        print('default_animal.jpg not found, aborting')
        return
    for name in COPIES:
        dest = os.path.join(MEDIA_IMG_DIR, name)
        try:
            shutil.copyfile(src, dest)
            print(f'Copied {src} -> {dest}')
        except Exception as e:
            print(f'Copy failed for {name}: {e}')

if __name__ == '__main__':
    main()