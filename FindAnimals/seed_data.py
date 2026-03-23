
import os
import django
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FindAnimals.settings')
django.setup()

from animalsdata.models import Park, Animal

def seed():
    User = get_user_model()
    
    # Create test user
    user, _ = User.objects.get_or_create(username='test_user', defaults={'nickname': '测试发现者'})
    
    # Create Parks
    parks_data = [
        {'name': '福州国家森林公园', 'address': '福建省福州市晋安区新店上赤桥', 'lng': 119.2965, 'lat': 26.1528, 'desc': '福州首个国家级森林公园，植被丰富'},
        {'name': '福州动物园', 'address': '福建省福州市晋安区新店镇', 'lng': 119.3005, 'lat': 26.1432, 'desc': '包含熊猫馆等多个动物展区'},
        {'name': '西湖公园', 'address': '福建省福州市鼓楼区湖滨路70号', 'lng': 119.2915, 'lat': 26.0963, 'desc': '福州保留最完整的古典园林'},
        {'name': '金牛山公园', 'address': '福建省福州市鼓楼区西洪路528号', 'lng': 119.2612, 'lat': 26.0885, 'desc': '福州现代化城市公园'},
    ]
    
    parks = []
    for p_data in parks_data:
        park, _ = Park.objects.get_or_create(
            name=p_data['name'],
            defaults={
                'address': p_data['address'],
                'lng': p_data['lng'],
                'lat': p_data['lat'],
                'description': p_data['desc'],
                'enabled': True
            }
        )
        parks.append(park)
        print(f"Created Park: {park.name}")

    # Create Animals
    animals_data = [
        {'name': '小熊猫', 'sname': 'Ailurus fulgens', 'desc': '在竹林里发现的一只可爱小熊猫', 'park': parks[0], 'views': 120},
        {'name': '赤腹松鼠', 'sname': 'Callosciurus erythraeus', 'desc': '树上跳来跳去很活跃', 'park': parks[0], 'views': 56},
        {'name': '黑天鹅', 'sname': 'Cygnus atratus', 'desc': '湖面上优雅游动', 'park': parks[2], 'views': 230},
        {'name': '白鹭', 'sname': 'Egretta garzetta', 'desc': '正在水边觅食', 'park': parks[3], 'views': 89},
        {'name': '金刚鹦鹉', 'sname': 'Ara', 'desc': '羽毛色彩斑斓', 'park': parks[1], 'views': 310},
    ]

    for a_data in animals_data:
        Animal.objects.get_or_create(
            name=a_data['name'],
            defaults={
                'scientific_name': a_data['sname'],
                'description': a_data['desc'],
                'park': a_data['park'],
                'discoverer': user,
                'audit_status': 'approved',
                'views_count': a_data['views'],
                'discovered_at': timezone.now() - timedelta(days=1),
                'audit_time': timezone.now(),
            }
        )
        print(f"Created Animal: {a_data['name']}")

if __name__ == '__main__':
    seed()
