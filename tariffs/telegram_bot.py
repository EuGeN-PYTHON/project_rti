import requests
import json
from django.conf import settings


def send_lead_to_telegram(lead):
    """
    Отправка заявки в Telegram чат
    """
    telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not telegram_bot_token or not telegram_chat_id:
        return False

    message = f"""
📋 *Новая заявка на подключение*

👤 *ФИО:* {lead.fio}
📞 *Телефон:* {lead.phone}
🏠 *Адрес:* {lead.address}
📊 *Тариф:* {lead.tariff.name}
📅 *Дата монтажа:* {lead.installation_date.strftime('%d.%m.%Y %H:%M') if lead.installation_date else 'Не назначена'}

🔗 *ID заявки:* {lead.id}
    """

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            lead.is_transferred_to_telegram = True
            lead.save()
            return True
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

    return False