from django.shortcuts import render, get_object_or_404
from .models import Region, Tariff


def index(request):
    # Получаем регион из middleware
    region = getattr(request, 'region', None)
    subdomain = getattr(request, 'subdomain', None)

    # Если регион определен по поддомену, показываем только его тарифы
    if region:
        tariffs = Tariff.objects.filter(region=region, region__is_active=True)
        regions = Region.objects.filter(is_active=True)
    else:
        # Если поддомена нет, показываем все регионы
        tariffs = Tariff.objects.filter(region__is_active=True)
        regions = Region.objects.filter(is_active=True)

    return render(request, "index.html", {
        "regions": regions,
        "tariffs": tariffs,
        "current_region": region,
        "current_subdomain": subdomain
    })


def region_redirect(request):
    """Перенаправление на поддомен региона"""
    region_id = request.GET.get('region')
    if region_id:
        try:
            region = Region.objects.get(id=region_id, is_active=True)
            # Перенаправляем на поддомен региона
            return redirect(f"http://{region.subdomain}.ваш-сайт.ru")
        except Region.DoesNotExist:
            pass
    return redirect('index')
