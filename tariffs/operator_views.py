import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Lead, Tariff, Region
from .telegram_bot import send_lead_to_telegram

# Логгер
logger = logging.getLogger(__name__)

# Добавляем логгер
logger = logging.getLogger(__name__)


def is_operator(user):
    return user.groups.filter(name='Operators').exists() or user.is_staff


@login_required
@user_passes_test(is_operator)
def operator_dashboard(request):
    """Дашборд оператора - ТОЛЬКО новые заявки"""
    new_leads = Lead.objects.filter(status='new').order_by('created_at')
    return render(request, 'operator/dashboard.html', {'new_leads': new_leads})


@login_required
@user_passes_test(is_operator)
def take_lead(request, lead_id):
    """Взять заявку в работу - сразу открываем форму редактирования"""
    lead = get_object_or_404(Lead, id=lead_id, status='new')

    # Назначаем оператора
    lead.operator = request.user
    lead.updated_at = timezone.now()
    lead.save()

    # Пробуем найти тарифы по региону заявки
    try:
        # Ищем регион по названию из заявки
        region = Region.objects.get(name=lead.region)
        tariffs = Tariff.objects.filter(region=region)
    except Region.DoesNotExist:
        # Если регион не найден, показываем все тарифы
        tariffs = Tariff.objects.all()

    # Если тарифов нет, показываем все доступные
    if not tariffs.exists():
        tariffs = Tariff.objects.all()

    print(f"Заявка: {lead.id}, Регион: '{lead.region}'")
    print(f"Найдено тарифов: {tariffs.count()}")

    return render(request, 'operator/edit_lead.html', {
        'lead': lead,
        'tariffs': tariffs,
        'status_choices': Lead.STATUS_CHOICES
    })


@login_required
@user_passes_test(is_operator)
def update_lead(request, lead_id):
    """Обновление заявки оператором с подробным логированием"""
    lead = get_object_or_404(Lead, id=lead_id, operator=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        installation_date = request.POST.get('installation_date')
        notes = request.POST.get('notes')
        tariff_id = request.POST.get('tariff')

        logger.info(f"📝 Обновление заявки #{lead.id} оператором {request.user.username}")
        logger.info(f"   Новый статус: {new_status}")
        logger.info(f"   Дата монтажа: {installation_date}")

        # Обновляем тариф если выбран новый
        if tariff_id:
            try:
                new_tariff = Tariff.objects.get(id=tariff_id)
                lead.tariff = new_tariff
                logger.info(f"   Тариф изменен на: {new_tariff.name}")
            except Tariff.DoesNotExist:
                logger.warning(f"   Попытка установить несуществующий тариф: {tariff_id}")
                messages.error(request, 'Выбран несуществующий тариф')

        # Обновляем статус
        if new_status in dict(Lead.STATUS_CHOICES):
            old_status = lead.status
            lead.status = new_status

            # Обновляем дату монтажа (может быть пустой)
            if installation_date:
                try:
                    lead.installation_date = timezone.datetime.strptime(installation_date, '%Y-%m-%dT%H:%M')
                    logger.info(f"   Дата монтажа установлена: {lead.installation_date}")
                except ValueError:
                    logger.error("   Неверный формат даты монтажа")
                    messages.error(request, 'Неверный формат даты')
            else:
                # Если дата очищена - устанавливаем None
                lead.installation_date = None
                logger.info("   Дата монтажа очищена")

            # Обновляем примечания
            if notes:
                lead.notes = notes
                logger.info("   Примечания обновлены")

            lead.updated_at = timezone.now()
            lead.save()

            logger.info(f"✅ Заявка #{lead.id} обновлена. Статус: {old_status} → {new_status}")

            # Если статус изменился на "Передано провайдеру"
            if new_status == 'transferred' and old_status != 'transferred':
                logger.info("🔄 Статус изменен на 'Передано провайдеру'")

                # ОТПРАВЛЯЕМ В TELEGRAM ДАЖЕ БЕЗ ДАТЫ МОНТАЖА
                logger.info("📋 Попытка отправки в Telegram...")
                telegram_success = send_lead_to_telegram(lead)

                if telegram_success:
                    messages.success(request, '✅ Заявка передана провайдеру и отправлена в Telegram!')
                    logger.info("✅ Уведомление об отправке в Telegram показано пользователю")
                else:
                    messages.warning(request,
                                     '⚠️ Заявка передана провайдеру, но не отправлена в Telegram. Проверьте настройки.')
                    logger.warning("⚠️ Показано предупреждение о проблеме с Telegram")

            else:
                messages.success(request, '✅ Изменения сохранены')
                logger.info("✅ Обычное уведомление об сохранении показано")

            return redirect('operator_dashboard')
        else:
            logger.error(f"❌ Неверный статус: {new_status}")
            messages.error(request, '❌ Неверный статус заявки')

    tariffs = Tariff.objects.all()
    return render(request, 'operator/edit_lead.html', {
        'lead': lead,
        'tariffs': tariffs,
        'status_choices': Lead.STATUS_CHOICES
    })

@login_required
@user_passes_test(is_operator)
def view_lead(request, lead_id):
    """Просмотр заявки (только чтение)"""
    lead = get_object_or_404(Lead, id=lead_id)
    return render(request, 'operator/view_lead.html', {'lead': lead})


@login_required
@user_passes_test(is_operator)
def search_leads(request):
    """Поиск заявок - ТОЛЬКО новые"""
    query = request.GET.get('q', '').strip()

    if query:
        leads = Lead.objects.filter(
            Q(fio__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query) |
            Q(notes__icontains=query),
            status='new'  # Только новые заявки
        ).order_by('-created_at')
    else:
        leads = Lead.objects.none()

    return render(request, 'operator/search_results.html', {
        'leads': leads,
        'query': query
    })