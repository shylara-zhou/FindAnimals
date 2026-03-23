#!/usr/bin/env python3
import os
import django
import sys

# 配置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FindAnimals.settings')
django.setup()
from animalsdata.models import Park

def update_park_covers():
    """更新公园封面图片路径"""
    print("开始更新公园封面路径...")
    
    # 公园信息
    parks = [
        {"id": 1, "name": "福州国家森林公园", "cover_file": "福州国家森林公园_cover.jpg"},
        {"id": 2, "name": "福州动物园", "cover_file": "福州动物园_cover.jpg"},
        {"id": 3, "name": "西湖公园", "cover_file": "西湖公园_cover.jpg"},
        {"id": 4, "name": "旗山公园", "cover_file": "旗山公园_cover.jpg"},
    ]
    
    for park_info in parks:
        park_id = park_info["id"]
        park_name = park_info["name"]
        cover_file = park_info["cover_file"]
        
        try:
            park = Park.objects.get(id=park_id)
            # 构建相对路径
            relative_path = f"park_covers/{cover_file}"
            # 更新公园封面
            park.cover = relative_path
            park.save()
            print(f"已更新公园 {park_name} 的封面图片路径")
        except Park.DoesNotExist:
            print(f"公园 ID {park_id} 不存在")
    
    print("公园封面路径更新完成！")

if __name__ == "__main__":
    update_park_covers()
