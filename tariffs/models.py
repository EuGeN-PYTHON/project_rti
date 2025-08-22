from django.db import models
from django.contrib.auth.models import User


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subdomain = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.subdomain:
            self.subdomain = self.generate_subdomain()
        super().save(*args, **kwargs)

    def generate_subdomain(self):
        """Генерация поддомена из названия региона"""
        name = self.name.lower().strip()
        mapping = {
            'москва': 'moskva',
            'санкт-петербург': 'spb',
            'краснодар': 'krasnodar',
            'самара': 'samara',
            'новосибирск': 'novosibirsk',
            'екатеринбург': 'ekaterinburg',
            'казань': 'kazan',
            'нижний новгород': 'nnovgorod',
        }
        return mapping.get(name, name.replace(' ', '-').replace('ё', 'e'))

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class Tariff(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="tariffs")
    name = models.CharField(max_length=100)
    speed = models.CharField(max_length=50, blank=True)
    price = models.PositiveIntegerField()
    # Новые поля
    interactive_tv = models.BooleanField(default=False, verbose_name='Интерактивное ТВ')
    online_cinema = models.BooleanField(default=False, verbose_name='Онлайн кинотеатр')
    mobile_data = models.PositiveIntegerField(default=0, verbose_name='Мобильные данные (ГБ)')
    mobile_minutes = models.PositiveIntegerField(default=0, verbose_name='Мобильные минуты')
    mobile_sms = models.PositiveIntegerField(default=0, verbose_name='Мобильные СМС')

    def __str__(self):
        return f"{self.name} ({self.region.name})"

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('repeated', 'Повторное обращение'),
        ('no_tech', 'Нет технической возможности'),
        ('transferred', 'Передано провайдеру'),
    ]

    fio = models.CharField(max_length=200, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес подключения')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name='Тариф')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    installation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата монтажа')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Оператор', related_name='leads')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    is_transferred_to_telegram = models.BooleanField(default=False, verbose_name='Передано в Telegram')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fio} - {self.tariff.name}"