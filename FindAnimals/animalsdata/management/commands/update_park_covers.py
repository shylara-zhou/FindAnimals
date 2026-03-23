from django.core.management.base import BaseCommand
from animalsdata.models import Park

class Command(BaseCommand):
    help = '更新公园封面图片路径'

    def handle(self, *args, **options):
        """更新公园封面图片路径"""
        self.stdout.write("开始更新公园封面路径...")
        
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
                self.stdout.write(f"已更新公园 {park_name} 的封面图片路径")
            except Park.DoesNotExist:
                self.stdout.write(f"公园 ID {park_id} 不存在")
        
        self.stdout.write("公园封面路径更新完成！")
