from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Проверить валидность Telegram токена'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

        if not token:
            self.stdout.write("❌ TELEGRAM_BOT_TOKEN не настроен!")
            return

        self.stdout.write(f"🔍 Проверка токена: {token[:10]}...")

        url = f"https://api.telegram.org/bot{token}/getMe"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data['result']
                    self.stdout.write("✅ Токен валиден!")
                    self.stdout.write(f"   Имя бота: {bot_info['first_name']}")
                    self.stdout.write(f"   Username: @{bot_info['username']}")
                    self.stdout.write(f"   ID бота: {bot_info['id']}")
                else:
                    self.stdout.write("❌ Неверный токен!")
                    self.stdout.write(f"   Ошибка: {data.get('description')}")
            else:
                self.stdout.write(f"❌ Ошибка HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.stdout.write(f"❌ Ошибка сети: {e}")