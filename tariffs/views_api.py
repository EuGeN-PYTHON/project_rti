from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Lead, Tariff, Region  # Добавляем импорт Region
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def create_lead(request):
    """
    Создание новой заявки из формы
    """
    try:
        logger.info("📥 Получен запрос на создание заявки")

        # Парсим JSON данные
        try:
            data = json.loads(request.body)
            logger.info(f"📋 Данные заявки: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return JsonResponse({'error': 'Неверный JSON'}, status=400)

        # Проверяем обязательные поля
        required_fields = ['fio', 'phone', 'address', 'tariff']
        missing_fields = []

        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                missing_fields.append(field)

        if missing_fields:
            logger.error(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            return JsonResponse({'error': f'Обязательные поля: {", ".join(missing_fields)}'}, status=400)

        # Получаем и проверяем тариф
        try:
            tariff_id = int(data['tariff'])
            tariff = Tariff.objects.get(id=tariff_id)
            logger.info(f"✅ Тариф найден: {tariff.name}")
        except (Tariff.DoesNotExist, ValueError) as e:
            logger.error(f"❌ Неверный тариф ID: {data.get('tariff')}, ошибка: {e}")
            return JsonResponse({'error': 'Неверный тариф'}, status=400)

        # Получаем регион из тарифа (основной способ)
        region = tariff.region
        logger.info(f"📍 Регион из тарифа: {region.name}")

        # Альтернативно: пытаемся найти регион по данным из формы
        region_name_from_form = data.get('region', '').strip()
        if region_name_from_form:
            try:
                # Очищаем название региона от лишних пробелов
                region_name_clean = ' '.join(region_name_from_form.split())
                # Пробуем найти регион по названию
                region_from_form = Region.objects.get(name=region_name_clean)
                region = region_from_form
                logger.info(f"📍 Регион из формы: {region.name}")
            except Region.DoesNotExist:
                logger.warning(f"⚠️ Регион '{region_name_clean}' не найден, используем регион тарифа")
            except Region.MultipleObjectsReturned:
                logger.warning(
                    f"⚠️ Найдено несколько регионов с именем '{region_name_clean}', используем регион тарифа")

        # Создаем заявку
        try:
            lead = Lead.objects.create(
                fio=data['fio'].strip(),
                phone=data['phone'].strip(),
                address=data['address'].strip(),
                tariff=tariff,
                region=region,  # Передаем объект Region
                notes=data.get('notes', '').strip()
            )

            logger.info(f"✅ Заявка создана: ID {lead.id}, ФИО: {lead.fio}, Регион: {region.name}")

            return JsonResponse({
                'success': True,
                'message': 'Заявка успешно создана',
                'lead_id': lead.id
            })

        except Exception as e:
            logger.error(f"❌ Ошибка при создании заявки: {e}")
            return JsonResponse({'error': 'Ошибка при создании заявки'}, status=500)

    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)