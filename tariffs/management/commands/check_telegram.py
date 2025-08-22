# management/commands/check_telegram.py
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Проверить настройки Telegram бота'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

        self.stdout.write("🔍 Проверка настроек Telegram:")
        self.stdout.write(f"   BOT_TOKEN: {'✅ установлен' if token else '❌ отсутствует'}")
        self.stdout.write(f"   CHAT_ID: {'✅ установлен' if chat_id else '❌ отсутствует'}")

        if token and chat_id:
            self.stdout.write("✅ Настройки Telegram в порядке!")
            self.stdout.write("   Для теста отправки используйте: python manage.py test_telegram")
        else:
            self.stdout.write("❌ Настройки Telegram неполные!")
            self.stdout.write("   Добавьте в settings.py:")
            self.stdout.write("   TELEGRAM_BOT_TOKEN = 'ваш_токен_бота'")
            self.stdout.write("   TELEGRAM_CHAT_ID = 'ваш_chat_id'")