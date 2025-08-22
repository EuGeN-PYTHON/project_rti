# tariffs/management/commands/get_chat_id_force.py
from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Принудительно получить chat_id через отправку сообщения'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

        if not token:
            self.stdout.write("❌ TELEGRAM_BOT_TOKEN не настроен!")
            return

        self.stdout.write("🔍 Принудительное получение chat_id...")
        self.stdout.write("1. Откройте Telegram")
        self.stdout.write("2. Найдите бота: @rti_lead_bot")
        self.stdout.write("3. Напишите любое сообщение")
        self.stdout.write("4. Нажмите Enter здесь чтобы продолжить...")

        input()  # Ждем пока пользователь отправит сообщение

        url = f"https://api.telegram.org/bot{token}/getUpdates"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if data.get('ok') and data.get('result'):
                    for update in data['result']:
                        if 'message' in update:
                            chat_id = update['message']['chat']['id']
                            chat_type = update['message']['chat']['type']

                            self.stdout.write(f"\n✅ Найден chat_id: {chat_id}")
                            self.stdout.write(f"   Тип чата: {chat_type}")

                            if chat_type == 'private':
                                user = update['message']['chat']
                                self.stdout.write(
                                    f"   Пользователь: {user.get('first_name', '')} {user.get('last_name', '')}")

                            self.stdout.write(f"\n📋 Добавьте в settings.py:")
                            self.stdout.write(f"TELEGRAM_CHAT_ID = '{chat_id}'")
                            return

                    self.stdout.write("❌ Сообщения не найдены. Убедитесь что:")
                    self.stdout.write("   - Бот @rti_lead_bot существует")
                    self.stdout.write("   - Вы отправили ему сообщение")
                    self.stdout.write("   - Бот не заблокирован")
                else:
                    self.stdout.write("❌ Нет обновлений. Проверьте токен.")
            else:
                self.stdout.write(f"❌ Ошибка HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.stdout.write(f"❌ Ошибка сети: {e}")