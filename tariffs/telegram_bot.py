import requests
import json
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_lead_to_telegram(lead):
    """
    Отправка заявки в Telegram чат с подробным логированием
    """
    logger.info(f"🔄 Попытка отправки заявки #{lead.id} в Telegram")

    # Проверяем настройки
    telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not telegram_bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return False

    if not telegram_chat_id:
        logger.error("❌ TELEGRAM_CHAT_ID не настроен в settings.py")
        return False

    logger.info(f"📋 Настройки Telegram: TOKEN={telegram_bot_token[:10]}..., CHAT_ID={telegram_chat_id}")

    # Формируем сообщение (дата монтажа может быть null)
    installation_date_info = ""
    if lead.installation_date:
        installation_date_info = f"📅 *Дата монтажа:* {lead.installation_date.strftime('%d.%m.%Y %H:%M')}"
    else:
        installation_date_info = "📅 *Дата монтажа:* Не назначена (требуется уточнить)"

    message = f"""
📋 *НОВАЯ ЗАЯВКА ПЕРЕДАНА ПРОВАЙДЕРУ*

👤 *ФИО:* {lead.fio}
📞 *Телефон:* {lead.phone}
🏠 *Адрес:* {lead.address}
📍 *Регион:* {lead.region}

📊 *Тариф:* {lead.tariff.name}
💰 *Цена:* {lead.tariff.price} ₽/мес
⚡ *Скорость:* {lead.tariff.speed or 'Не указана'}

{installation_date_info}
👨‍💼 *Оператор:* {lead.operator.username if lead.operator else 'Не назначен'}

🔗 *ID заявки:* {lead.id}
⏰ *Создана:* {lead.created_at.strftime('%d.%m.%Y %H:%M')}

💡 *Примечание:* Дата монтажа будет согласована дополнительно
    """

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        logger.info(f"📤 Отправка запроса к Telegram API...")
        response = requests.post(url, json=payload, timeout=10)

        logger.info(f"📩 Ответ от Telegram: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Заявка #{lead.id} успешно отправлена в Telegram!")
                lead.is_transferred_to_telegram = True
                lead.save()
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                logger.error(f"❌ Ошибка Telegram API: {error_msg}")
                return False
        else:
            logger.error(f"❌ HTTP ошибка {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сети при отправке в Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False