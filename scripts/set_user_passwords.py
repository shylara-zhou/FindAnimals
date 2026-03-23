#!/usr/bin/env python3
import os
import sys

# 配置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FindAnimals.FindAnimals.settings')

import django
django.setup()

from django.contrib.auth import get_user_model


def set_user_passwords():
    """为所有现有用户设置密码为123456"""
    print("开始为现有用户设置密码...")
    
    User = get_user_model()
    users = User.objects.all()
    
    for user in users:
        user.set_password('123456')
        user.save()
        print(f"已为用户 {user.username} 设置密码为 123456")
    
    print(f"共为 {users.count()} 个用户设置了密码")

if __name__ == "__main__":
    set_user_passwords()
