# admin.py
from django.contrib import admin
from .models import Lead, Tariff, Region
from .admin_export import export_leads_to_excel, export_all_leads_to_excel, export_filtered_leads


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'fio', 'phone', 'region', 'tariff',
        'status', 'created_at', 'operator'
    ]
    list_filter = ['status', 'region', 'created_at', 'operator']
    search_fields = ['fio', 'phone', 'address', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    actions = [export_leads_to_excel, export_all_leads_to_excel, export_filtered_leads]

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Добавляем действие для экспорта всех заявок
        actions['export_all_leads_to_excel'] = (
            export_all_leads_to_excel,
            'export_all_leads_to_excel',
            export_all_leads_to_excel.short_description
        )
        return actions


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'price', 'speed', 'interactive_tv', 'online_cinema']
    list_filter = ['region', 'interactive_tv', 'online_cinema']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'is_active']
    list_filter = ['is_active']