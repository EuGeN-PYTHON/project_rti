# management/commands/test_telegram.py
from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Тест отправки сообщения в Telegram'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

        if not token or not chat_id:
            self.stdout.write("❌ Настройки Telegram не настроены!")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': '✅ Тестовое сообщение от Django бота\nЭто значит, что настройки работают!',
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.stdout.write("✅ Тестовое сообщение отправлено успешно!")
            else:
                self.stdout.write(f"❌ Ошибка: {response.status_code} - {response.text}")
        except Exception as e:
            self.stdout.write(f"❌ Ошибка сети: {e}")