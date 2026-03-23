from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = '为所有现有用户设置密码为123456'

    def handle(self, *args, **options):
        """为所有现有用户设置密码为123456"""
        self.stdout.write("开始为现有用户设置密码...")
        
        User = get_user_model()
        users = User.objects.all()
        
        for user in users:
            user.set_password('123456')
            user.save()
            self.stdout.write(f"已为用户 {user.username} 设置密码为 123456")
        
        self.stdout.write(f"共为 {users.count()} 个用户设置了密码")
