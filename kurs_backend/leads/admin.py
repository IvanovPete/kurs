from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'login', 'yandex_id', 'age', 'start_english_level', 'group',
                    'payments', 'attendance', 'telegram', 'vk', 'yandex', 'created_at')
    list_filter = ('created_at', 'start_english_level', 'age', 'group')
    search_fields = ('phone', 'login', 'yandex_id',
                     'telegram', 'vk', 'yandex', 'group')
    fieldsets = (
        ('Основная информация', {
            'fields': ('phone', 'login', 'yandex_id', 'age', 'start_english_level')
        }),
        ('Соцсети для связи', {
            'fields': ('telegram', 'vk', 'yandex'),
            'description': 'Заполните хотя бы одну соцсеть (необязательно)'
        }),
        ('Управление лидами (только для админа)', {
            'fields': ('group', 'payments', 'attendance'),
            'description': 'Эти поля заполняются только вручную через админку'
        }),
    )
