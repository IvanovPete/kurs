from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'login', 'yandex_id', 'email', 'first_name', 'last_name',
                    'sex', 'birthday', 'avatar_url', 'age', 'start_english_level',
                    'group', 'payments', 'attendance', 'telegram', 'vk', 'yandex',
                    'free_lessons', 'created_at')
    list_filter = ('created_at', 'start_english_level', 'age', 'group', 'sex')
    search_fields = ('phone', 'login', 'yandex_id', 'email', 'first_name',
                     'last_name', 'telegram', 'vk', 'yandex', 'group')
    fieldsets = (
        ('Данные от Яндекса', {
            'fields': ('yandex_id', 'login', 'email', 'first_name', 'last_name',
                       'sex', 'birthday', 'avatar_url'),
            'description': 'Информация, полученная от Яндекса при входе'
        }),
        ('Основная информация', {
            'fields': ('phone', 'age', 'start_english_level', 'free_lessons')
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
 