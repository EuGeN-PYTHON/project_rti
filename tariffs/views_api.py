from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Lead, Tariff
from .telegram_bot import send_lead_to_telegram


@csrf_exempt
@require_POST
def create_lead(request):
    try:
        data = json.loads(request.body)

        required_fields = ['fio', 'phone', 'address', 'tariff']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return JsonResponse({'error': f'Поле {field} обязательно'}, status=400)

        try:
            tariff = Tariff.objects.get(id=int(data['tariff']))
        except (Tariff.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Неверный тариф'}, status=400)

        lead = Lead.objects.create(
            fio=data['fio'].strip(),
            phone=data['phone'].strip(),
            address=data['address'].strip(),
            tariff=tariff,
            region=data.get('region', ''),
            notes=data.get('notes', '')
        )

        return JsonResponse({
            'success': True,
            'message': 'Заявка успешно создана',
            'lead_id': lead.id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Ошибка сервера'}, status=500)