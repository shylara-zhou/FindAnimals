#!/usr/bin/env python3
import os
import requests

# 媒体目录路径
MEDIA_ROOT = r'd:\PycharmProjects\FindAnimals\media'
PARK_COVERS_DIR = os.path.join(MEDIA_ROOT, 'park_covers')

# 确保目录存在
os.makedirs(PARK_COVERS_DIR, exist_ok=True)

# 公园信息
parks = [
    {
        "id": 1,
        "name": "福州国家森林公园",
        "prompt": "福州国家森林公园，绿色植被茂密，参天大树，阳光透过树叶，自然风景，高清照片"
    },
    {
        "id": 2,
        "name": "福州动物园",
        "prompt": "福州动物园，动物笼舍，游客参观，大象，长颈鹿，动物园景观，高清照片"
    },
    {
        "id": 3,
        "name": "西湖公园",
        "prompt": "福州西湖公园，湖泊，亭台楼阁，拱桥，柳树，游客，园林景观，高清照片"
    },
    {
        "id": 4,
        "name": "旗山公园",
        "prompt": "福州旗山公园，现代公园，草坪，花卉，休闲设施，游客，高清照片"
    }
]

def generate_image(prompt, park_name):
    """生成公园封面图片"""
    print(f"生成 {park_name} 的封面图片...")
    # 使用Trae API生成图片
    url = f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt}&image_size=landscape_16_9"
    response = requests.get(url)
    
    if response.status_code == 200:
        # 保存图片
        file_name = f"{park_name.replace(' ', '_')}_cover.jpg"
        file_path = os.path.join(PARK_COVERS_DIR, file_name)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"图片已保存到: {file_path}")
        return file_name
    else:
        print(f"生成图片失败: {response.status_code}")
        return None

def main():
    """主函数"""
    print("开始生成公园封面图片...")
    
    for park_info in parks:
        park_name = park_info["name"]
        prompt = park_info["prompt"]
        
        # 生成图片
        generate_image(prompt, park_name)
    
    print("公园封面图片生成完成！")
    print("\n请手动更新数据库中的公园封面路径:")
    print("路径格式: park_covers/公园名称_cover.jpg")

if __name__ == "__main__":
    main()
