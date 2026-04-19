from django.db import models

class Lead(models.Model):
    phone = models.CharField('Номер телефона', max_length=20)  # обязательное поле
    
    # Отдельные необязательные поля для каждой соцсети
    telegram = models.CharField('Telegram', max_length=100, blank=True, null=True)
    vk = models.CharField('VK', max_length=100, blank=True, null=True)
    yandex = models.CharField('Яндекс Мессенджер', max_length=100, blank=True, null=True)

    group = models.CharField('Группа', max_length=100, blank=True, null=True)
    start_english_level = models.CharField('Начальный уровень английского', max_length=50, blank=True, null=True)

    payments = models.CharField('Платежи', max_length=100, blank=True, null=True)  # для хранения информации о платежах, если нужно
    attendance = models.CharField('Посещаемость', max_length=100, blank=True, null=True)  # для хранения информации о посещаемости, если нужно

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
    
    def __str__(self):
        return f'{self.phone} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'