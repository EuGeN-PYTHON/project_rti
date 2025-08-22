from django.contrib import admin
from .models import Region, Tariff, Lead

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'is_active')
    list_editable = ('is_active',)

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'speed', 'price', 'interactive_tv', 'online_cinema')
    list_filter = ('region', 'interactive_tv', 'online_cinema')
    list_editable = ('price', 'interactive_tv', 'online_cinema')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('fio', 'phone', 'tariff', 'region', 'status', 'operator', 'installation_date', 'created_at')
    list_filter = ('status', 'region', 'created_at', 'operator')
    search_fields = ('fio', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'