import requests
import json
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_new_lead_notification(lead):
    """
    Отправка уведомления о новой заявке в Telegram чат
    """
    logger.info(f"🔄 Попытка отправки уведомления о новой заявке #{lead.id} в Telegram")

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

    # Конвертируем время в московский часовой пояс
    moscow_time = timezone.localtime(lead.created_at)

    # Детальная информация о мобильной связи
    mobile_details = []
    if lead.tariff.mobile_data > 0:
        mobile_details.append(f"📊 *Мобильный интернет:* {lead.tariff.mobile_data} ГБ")
    if lead.tariff.mobile_minutes > 0:
        mobile_details.append(f"🎧 *Минуты:* {lead.tariff.mobile_minutes}")
    if lead.tariff.mobile_sms > 0:
        mobile_details.append(f"💬 *SMS:* {lead.tariff.mobile_sms}")

    # Формируем блок мобильной связи
    mobile_info = ""
    if mobile_details:
        mobile_info = "\n".join(mobile_details) + "\n"
    else:
        mobile_info = "📱 *Мобильная связь:* ❌\n"

    # Формируем сообщение о новой заявке
    message = f"""
🚨 *НОВАЯ ЗАЯВКА С САЙТА*

👤 *ФИО:* {lead.fio}
📞 *Телефон:* {lead.phone}
🏠 *Адрес:* {lead.address}
📍 *Регион:* {lead.region.name if hasattr(lead.region, 'name') else lead.region}

📊 *Тариф:* {lead.tariff.name}
💰 *Цена:* {lead.tariff.price} ₽/мес
⚡ *Скорость интернета:* {lead.tariff.speed or 'Не указана'}

📺 *Интерактивное ТВ:* {'✅' if lead.tariff.interactive_tv else '❌'}
🎬 *Онлайн-кинотеатр:* {'✅' if lead.tariff.online_cinema else '❌'}

{mobile_info}
🔗 *ID заявки:* {lead.id}
⏰ *Создана:* {moscow_time.strftime('%d.%m.%Y %H:%M')} (МСК)
📊 *Статус:* Новая

💡 *Требуется обработать в панели оператора*
    """

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        logger.info(f"📤 Отправка уведомления о новой заявке к Telegram API...")
        response = requests.post(url, json=payload, timeout=10)

        logger.info(f"📩 Ответ от Telegram: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Уведомление о новой заявке #{lead.id} успешно отправлено в Telegram!")
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


def send_lead_to_telegram(lead):
    """
    Отправка заявки в Telegram чат с подробным логированием (при передаче провайдеру)
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

    # Конвертируем время в московский часовой пояс
    created_moscow = timezone.localtime(lead.created_at)
    updated_moscow = timezone.localtime(lead.updated_at)

    # Формируем сообщение (дата монтажа может быть null)
    installation_date_info = ""
    if lead.installation_date:
        installation_moscow = timezone.localtime(lead.installation_date)
        installation_date_info = f"📅 *Дата монтажа:* {installation_moscow.strftime('%d.%m.%Y %H:%M')} (МСК)"
    else:
        installation_date_info = "📅 *Дата монтажа:* Не назначена (требуется уточнить)"

    # Детальная информация о мобильной связи
    mobile_details = []
    if lead.tariff.mobile_data > 0:
        mobile_details.append(f"📊 *Мобильный интернет:* {lead.tariff.mobile_data} ГБ")
    if lead.tariff.mobile_minutes > 0:
        mobile_details.append(f"🎧 *Минуты:* {lead.tariff.mobile_minutes}")
    if lead.tariff.mobile_sms > 0:
        mobile_details.append(f"💬 *SMS:* {lead.tariff.mobile_sms}")

    # Формируем блок мобильной связи
    mobile_info = ""
    if mobile_details:
        mobile_info = "\n".join(mobile_details) + "\n"
    else:
        mobile_info = "📱 *Мобильная связь:* ❌\n"

    message = f"""
📋 *ЗАЯВКА ПЕРЕДАНА ПРОВАЙДЕРУ*

👤 *ФИО:* {lead.fio}
📞 *Телефон:* {lead.phone}
🏠 *Адрес:* {lead.address}
📍 *Регион:* {lead.region.name if hasattr(lead.region, 'name') else lead.region}

📊 *Тариф:* {lead.tariff.name}
💰 *Цена:* {lead.tariff.price} ₽/мес
⚡ *Скорость интернета:* {lead.tariff.speed or 'Не указана'}

📺 *Интерактивное ТВ:* {'✅' if lead.tariff.interactive_tv else '❌'}
🎬 *Онлайн-кинотеатр:* {'✅' if lead.tariff.online_cinema else '❌'}

{mobile_info}
{installation_date_info}
👨‍💼 *Оператор:* {lead.operator.username if lead.operator else 'Не назначен'}

🔗 *ID заявки:* {lead.id}
⏰ *Создана:* {created_moscow.strftime('%d.%m.%Y %H:%M')} (МСК)
🔄 *Обновлена:* {updated_moscow.strftime('%d.%m.%Y %H:%M')} (МСК)

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


def send_operator_notification(lead, operator_name, action):
    """
    Отправка уведомления о действиях оператора
    """
    logger.info(f"🔄 Попытка отправки уведомления о действии оператора #{lead.id}")

    telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not telegram_bot_token or not telegram_chat_id:
        return False

    moscow_time = timezone.localtime(timezone.now())

    action_messages = {
        'taken': f"👨‍💼 *Оператор {operator_name} взял заявку в работу*",
        'updated': f"✏️ *Оператор {operator_name} обновил заявку*",
        'completed': f"✅ *Оператор {operator_name} завершил обработку заявки*"
    }

    message = f"""
{action_messages.get(action, '🔔 *Действие с заявкой*')}

👤 *Клиент:* {lead.fio}
📞 *Телефон:* {lead.phone}
🔗 *ID заявки:* {lead.id}
📊 *Статус:* {lead.get_status_display()}
⏰ *Время:* {moscow_time.strftime('%d.%m.%Y %H:%M')} (МСК)
    """

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False


def send_error_notification(error_message, context=None):
    """
    Отправка уведомления об ошибке
    """
    telegram_bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not telegram_bot_token or not telegram_chat_id:
        return False

    moscow_time = timezone.localtime(timezone.now())

    message = f"""
🚨 *ОШИБКА В СИСТЕМЕ*

⏰ *Время:* {moscow_time.strftime('%d.%m.%Y %H:%M')} (МСК)
❌ *Ошибка:* {error_message}
    """

    if context:
        message += f"\n📋 *Контекст:* {context}"

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        'chat_id': telegram_chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False