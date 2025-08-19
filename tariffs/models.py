from django.db import models

# Create your models here.

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tariff(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="tariffs")
    name = models.CharField(max_length=100)
    speed = models.CharField(max_length=50, blank=True)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.region.name})"

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('contacted', 'Связались'),
        ('processed', 'Обработана'),
        ('rejected', 'Отклонена'),
    ]
    
    fio = models.CharField(max_length=200, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес подключения')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name='Тариф')
    region = models.CharField(max_length=100, verbose_name='Регион')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.fio} - {self.tariff.name}"

