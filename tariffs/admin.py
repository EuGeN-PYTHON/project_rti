from django.contrib import admin
from .models import Region, Tariff, Lead

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'speed', 'price')
    list_filter = ('region',)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('fio', 'phone', 'tariff', 'region', 'status', 'created_at')
    list_filter = ('status', 'region', 'created_at')
    search_fields = ('fio', 'phone', 'address')
    readonly_fields = ('created_at',)
