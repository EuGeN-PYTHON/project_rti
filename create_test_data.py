import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rti_project.settings')
django.setup()

from tariffs.models import Region, Tariff


def create_test_data():
    # Создаем регионы
    regions_data = [
        {'name': 'Москва', 'subdomain': 'moskva'},
        {'name': 'Самара', 'subdomain': 'samara'},
        {'name': 'Краснодар', 'subdomain': 'krasnodar'},
    ]

    for data in regions_data:
        region, created = Region.objects.get_or_create(
            name=data['name'],
            defaults={'subdomain': data['subdomain']}
        )
        if created:
            print(f'Создан регион: {region.name}')

    # Создаем тарифы для Москвы
    moscow = Region.objects.get(name='Москва')
    tariffs_data = [
        {
            'name': 'Стандарт', 'speed': '100 Мбит/с', 'price': 500,
            'interactive_tv': True, 'online_cinema': False,
            'mobile_data': 10, 'mobile_minutes': 200, 'mobile_sms': 50
        },
        {
            'name': 'Премиум', 'speed': '300 Мбит/с', 'price': 800,
            'interactive_tv': True, 'online_cinema': True,
            'mobile_data': 20, 'mobile_minutes': 500, 'mobile_sms': 100
        },
        {
            'name': 'Максимум', 'speed': '500 Мбит/с', 'price': 1200,
            'interactive_tv': True, 'online_cinema': True,
            'mobile_data': 30, 'mobile_minutes': 1000, 'mobile_sms': 200
        },
    ]

    for data in tariffs_data:
        tariff, created = Tariff.objects.get_or_create(
            region=moscow,
            name=data['name'],
            defaults=data
        )
        if created:
            print(f'Создан тариф: {tariff.name}')


if __name__ == '__main__':
    create_test_data()