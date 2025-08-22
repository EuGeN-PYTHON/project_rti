from django.http import Http404
from django.shortcuts import redirect  # Добавляем импорт
from django.urls import reverse
from tariffs.models import Region


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.region_map = {}  # Кэш регионов

    def __call__(self, request):
        # Получаем поддомен из запроса
        host = request.get_host()
        subdomain = self.get_subdomain(host)

        # Определяем регион по поддомену
        request.region = self.get_region_from_subdomain(subdomain)
        request.subdomain = subdomain

        response = self.get_response(request)
        return response

    def get_subdomain(self, host):
        """Извлекаем поддомен из хоста"""
        # Для localhost разработки
        if 'localhost' in host or '127.0.0.1' in host:
            parts = host.split('.')
            if len(parts) >= 2 and parts[0] != '127':
                return parts[0].lower()
            return None  # Основной localhost без поддомена

        # Для production
        parts = host.split('.')
        if len(parts) >= 3:
            return parts[0].lower()
        return None

    def get_region_from_subdomain(self, subdomain):
        """Сопоставляем поддомен с регионом"""
        if not subdomain:
            return None

        # Кэшируем запросы к БД
        if subdomain not in self.region_map:
            try:
                # Приводим к стандартному названию
                region_name = self.normalize_region_name(subdomain)
                region = Region.objects.get(name__iexact=region_name)
                self.region_map[subdomain] = region
            except Region.DoesNotExist:
                self.region_map[subdomain] = None

        return self.region_map[subdomain]

    def normalize_region_name(self, subdomain):
        """Приводим поддомен к нормальному названию региона"""
        mapping = {
            'moskva': 'Москва',
            'spb': 'Санкт-Петербург',
            'krasnodar': 'Краснодар',
            'samara': 'Самара',
            'novosibirsk': 'Новосибирск',
            'ekaterinburg': 'Екатеринбург',
            'kazan': 'Казань',
            'nnovgorod': 'Нижний Новгород',
            'test': 'Москва'  # для тестирования
        }

        return mapping.get(subdomain, subdomain.capitalize())


class OperatorAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, пытается ли пользователь получить доступ к операторской панели
        if request.path.startswith('/operator/') and not request.user.is_authenticated:
            return redirect(f'{reverse("login")}?next={request.path}')

        # Проверяем, аутентифицирован ли пользователь и является ли оператором
        if request.path.startswith('/operator/') and request.user.is_authenticated:
            if not (request.user.groups.filter(name='Operators').exists() or request.user.is_staff):
                return redirect('/admin/')  # Перенаправляем в админку если не оператор

        response = self.get_response(request)
        return response