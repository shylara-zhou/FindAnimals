from PIL import Image, ImageDraw

def make_icon(filename, draw_func, active=False):
    size = 81
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    color = (22, 163, 74, 255) if active else (156, 163, 175, 255)
    draw_func(d, color, size)
    img.save(filename)

# 探索 - 更精致的指南针（加N/S标识+加粗指针）
def draw_explore(d, c, s):
    cx, cy = s//2, s//2
    r = s//2 - 6
    # 外圈（双环）
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=3)
    d.ellipse([cx-r+5, cy-r+5, cx+r-5, cy+r-5], outline=c, width=1)
    # 北指针（三角，色深）
    pts_n = [
        (cx, cy-r+8),
        (cx-8, cy-2),
        (cx, cy+2),
        (cx+8, cy-2)
    ]
    d.polygon(pts_n, fill=c)
    # 南指针（较浅三角）
    c2 = (c[0], c[1], c[2], 160)
    pts_s = [
        (cx, cy+r-8),
        (cx-8, cy+2),
        (cx, cy-2),
        (cx+8, cy+2)
    ]
    d.polygon(pts_s, fill=c2)
    # N标识
    d.text((cx-3, cy-r+1), 'N', fill=c)
    # 中心圆
    d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=(255,255,255,255), outline=c, width=2)

# 排行 - 奖杯（加星标+杯身细节）
def draw_rank(d, c, s):
    cx = s//2
    top = 10
    cup_h = 34
    cup_w = 34
    # 杯子主体（填充+描边）
    cup_body = [
        (cx-cup_w//2, top),
        (cx+cup_w//2, top),
        (cx+cup_w//2-5, top+cup_h),
        (cx-cup_w//2+5, top+cup_h)
    ]
    d.polygon(cup_body, outline=c, width=3, fill=None)
    # 把手左
    d.arc([cx-cup_w//2-11, top+5, cx-cup_w//2+9, top+cup_h-13], start=90, end=270, fill=c, width=3)
    # 把手右
    d.arc([cx+cup_w//2-9, top+5, cx+cup_w//2+11, top+cup_h-13], start=270, end=90, fill=c, width=3)
    # 星星在杯口上
    star_cx, star_cy = cx, top-3
    star_r = 5
    # 五角星
    import math
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i*36)
        rr = star_r if i%2==0 else star_r*0.45
        pts.append((star_cx + rr*math.cos(angle), star_cy + rr*math.sin(angle)))
    d.polygon(pts, fill=c)
    # 底座梯形
    d.polygon([
        (cx-11, top+cup_h),
        (cx+11, top+cup_h),
        (cx+15, top+cup_h+7),
        (cx-15, top+cup_h+7)
    ], fill=c)
    # 底座
    d.rectangle([cx-17, top+cup_h+7, cx+17, top+cup_h+13], fill=c)

# 我的 - 用户（加小笑脸+圆润身体）
def draw_mine(d, c, s):
    cx = s//2
    # 头
    head_r = 12
    head_cy = 27
    d.ellipse([cx-head_r, head_cy-head_r, cx+head_r, head_cy+head_r], outline=c, width=3)
    # 眼睛
    eye_r = 1.5
    d.ellipse([cx-5-eye_r, head_cy-2-eye_r, cx-5+eye_r, head_cy-2+eye_r], fill=c)
    d.ellipse([cx+5-eye_r, head_cy-2-eye_r, cx+5+eye_r, head_cy-2+eye_r], fill=c)
    # 微笑嘴
    d.arc([cx-4, head_cy+1, cx+4, head_cy+7], start=0, end=180, fill=c, width=2)
    # 肩膀/身体（圆弧+连接到头的线）
    body_top = head_cy + head_r - 1
    d.line([cx-head_r+2, body_top, cx-20, body_top+12], fill=c, width=3)
    d.line([cx+head_r-2, body_top, cx+20, body_top+12], fill=c, width=3)
    d.arc([cx-22, body_top+4, cx+22, s-2], start=195, end=345, fill=c, width=3)

base = r'd:\PycharmProjects\FindAnimals\fztujian\fztujian\images\tab'

import os
os.makedirs(base, exist_ok=True)

for active in [False, True]:
    suffix = '_active' if active else ''
    make_icon(f'{base}/explore{suffix}.png', draw_explore, active=active)
    make_icon(f'{base}/rank{suffix}.png', draw_rank, active=active)
    make_icon(f'{base}/mine{suffix}.png', draw_mine, active=active)

print('icons generated')
