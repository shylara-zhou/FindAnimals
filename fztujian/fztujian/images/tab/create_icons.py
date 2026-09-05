import struct
import zlib
import os

def create_png(width, height, color, filepath):
    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    
    raw_data = b''
    cx, cy = width // 2, height // 2
    r = width // 2 - 3
    for y in range(height):
        raw_data += b'\x00'
        for x in range(width):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= r:
                raw_data += bytes(color)
            else:
                raw_data += b'\x00\x00\x00'
    
    compressed = zlib.compress(raw_data, 9)
    
    with open(filepath, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(make_chunk(b'IHDR', ihdr))
        f.write(make_chunk(b'IDAT', compressed))
        f.write(make_chunk(b'IEND', b''))

os.chdir(r'd:\PycharmProjects\FindAnimals\fztujian\fztujian\images\tab')

# 灰色图标 (未选中) - 48x48
create_png(48, 48, [153, 153, 153], 'explore.png')
create_png(48, 48, [153, 153, 153], 'rank.png')
create_png(48, 48, [153, 153, 153], 'mine.png')

# 绿色图标 (选中) - 48x48
create_png(48, 48, [26, 173, 25], 'explore_active.png')
create_png(48, 48, [26, 173, 25], 'rank_active.png')
create_png(48, 48, [26, 173, 25], 'mine_active.png')

print('Icons created successfully')
