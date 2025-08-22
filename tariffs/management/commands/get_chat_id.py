from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import time


class Command(BaseCommand):
    help = 'Получить chat_id из Telegram'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

        if not token:
            self.stdout.write("❌ TELEGRAM_BOT_TOKEN не настроен!")
            self.stdout.write("Добавьте в settings.py: TELEGRAM_BOT_TOKEN = 'ваш_токен'")
            return

        self.stdout.write("🔄 Получение обновлений от Telegram...")
        self.stdout.write("📝 Отправьте сообщение вашему боту в Telegram")

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
                            chat_title = update['message']['chat'].get('title', 'Личный чат')

                            self.stdout.write(f"\n✅ Найден chat_id:")
                            self.stdout.write(f"   CHAT_ID: {chat_id}")
                            self.stdout.write(f"   Тип: {chat_type}")
                            self.stdout.write(f"   Название: {chat_title}")

                            if chat_type == 'private':
                                self.stdout.write(f"   Пользователь: {update['message']['chat']['first_name']}")

                            self.stdout.write(f"\n📋 Добавьте в settings.py:")
                            self.stdout.write(f"TELEGRAM_CHAT_ID = '{chat_id}'")
                            return

                    self.stdout.write("❌ Не найдено сообщений. Отправьте боту сообщение и попробуйте снова.")
                else:
                    self.stdout.write("❌ Нет обновлений. Отправьте боту сообщение и попробуйте снова.")
            else:
                self.stdout.write(f"❌ Ошибка HTTP {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            self.stdout.write(f"❌ Ошибка сети: {e}")
        except Exception as e:
            self.stdout.write(f"❌ Неожиданная ошибка: {e}")