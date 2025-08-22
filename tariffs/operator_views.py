from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from .models import Lead, Tariff, Region
from .telegram_bot import send_lead_to_telegram
from django.http import JsonResponse


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
    """Обновление заявки оператором"""
    lead = get_object_or_404(Lead, id=lead_id, operator=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        installation_date = request.POST.get('installation_date')
        notes = request.POST.get('notes')
        tariff_id = request.POST.get('tariff')
        stay_on_page = request.POST.get('stay_on_page')

        # Обновляем тариф если выбран новый
        if tariff_id:
            try:
                new_tariff = Tariff.objects.get(id=tariff_id)
                lead.tariff = new_tariff
            except Tariff.DoesNotExist:
                pass

        # Обновляем статус
        if new_status in dict(Lead.STATUS_CHOICES):
            lead.status = new_status

            # Обновляем дату монтажа
            if installation_date:
                try:
                    lead.installation_date = timezone.datetime.strptime(installation_date, '%Y-%m-%dT%H:%M')
                except:
                    pass

            # Обновляем примечания
            if notes:
                lead.notes = notes

            lead.updated_at = timezone.now()
            lead.save()

            # Если статус "Передано провайдеру" - отправляем в Telegram
            if new_status == 'transferred' and lead.installation_date:
                send_lead_to_telegram(lead)

            # Если AJAX запрос (остаться на странице)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or stay_on_page:
                return JsonResponse({'success': True, 'message': 'Изменения сохранены'})

            messages.success(request, 'Заявка обновлена')
            return redirect('operator_dashboard')

    # Если AJAX запрос с ошибкой
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Ошибка при сохранении'})

    tariffs = Tariff.objects.filter(region__name=lead.region)
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
    query = request.GET.get('q', '')

    if query:
        leads = Lead.objects.filter(
            Q(fio__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query) |
            Q(notes__icontains=query),
            status='new'
        ).order_by('-created_at')
    else:
        leads = Lead.objects.none()

    return render(request, 'operator/search_results.html', {
        'leads': leads,
        'query': query
    })