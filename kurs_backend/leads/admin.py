from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('phone', 'telegram', 'vk', 'yandex', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('phone', 'telegram', 'vk', 'yandex')
    fieldsets = (
        ('Основная информация', {
            'fields': ('phone',)
        }),
        ('Соцсети для связи', {
            'fields': ('telegram', 'vk', 'yandex'),
            'description': 'Заполните хотя бы одну соцсеть (необязательно)'
        }),
    )