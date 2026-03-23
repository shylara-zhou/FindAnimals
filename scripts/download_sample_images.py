import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_IMG_DIR = os.path.join(BASE_DIR, 'media', 'img')

SAMPLES = {
    'default_animal.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg',
    # Real animal images from Wikimedia Commons (free to use)
    'panda.jpg': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Grosser_Panda.JPG',
    'lion.jpg': 'https://upload.wikimedia.org/wikipedia/commons/7/73/Lion_waiting_in_Namibia.jpg',
    'tiger.jpg': 'https://upload.wikimedia.org/wikipedia/commons/5/56/Tiger.50.jpg',
    'elephant.jpg': 'https://upload.wikimedia.org/wikipedia/commons/6/63/African_Bush_Elephant.jpg',
    'giraffe.jpg': 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Giraffa_camelopardalis_reticulata.jpg',
    'zebra.jpg': 'https://upload.wikimedia.org/wikipedia/commons/2/26/Grant%27s_Zebra.jpg',
    # Park cover samples (scenic, general-purpose)
    'park_default.jpg': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/Green_park_landscape.jpg',
    'park_forest.jpg': 'https://upload.wikimedia.org/wikipedia/commons/6/6d/Forest_in_Finland_2012.jpg',
    'park_lake.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/3c/Lake_and_park.jpg',
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def download(url, dest):
    print(f'Downloading {url} -> {dest}')
    # Add basic headers to avoid some servers blocking default User-Agent
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp, open(dest, 'wb') as f:
        f.write(resp.read())

def main():
    ensure_dir(MEDIA_IMG_DIR)
    for filename, url in SAMPLES.items():
        dest = os.path.join(MEDIA_IMG_DIR, filename)
        try:
            download(url, dest)
        except Exception as e:
            print(f'Failed to download {filename}: {e}')

if __name__ == '__main__':
    main()