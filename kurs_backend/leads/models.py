from django.db import models


class User(models.Model):
    phone = models.CharField(
        'Номер телефона', max_length=20, blank=True, null=True)
    email = models.EmailField('Почта', max_length=100, blank=True, null=True)
    yandex_id = models.CharField(
        'Яндекс ID', max_length=100, unique=True, blank=True, null=True)
    login = models.CharField('Логин', max_length=100, blank=True, null=True)
    password = models.CharField(
        'Пароль', max_length=128, blank=True, null=True)
    first_name = models.CharField('Имя', max_length=100, blank=True, null=True)
    last_name = models.CharField(
        'Фамилия', max_length=100, blank=True, null=True)
    sex = models.CharField('Пол', max_length=10, blank=True, null=True)
    birthday = models.CharField(
        'Дата рождения', max_length=20, blank=True, null=True)
    avatar_url = models.URLField(
        'Аватар URL', max_length=500, blank=True, null=True)
    age = models.CharField(
        'Возраст ребёнка', max_length=10, blank=True, null=True)
    free_lessons = models.IntegerField(
        'Количество бесплатных занятий', blank=True, null=True)

    # Отдельные необязательные поля для каждой соцсети
    telegram = models.CharField(
        'Telegram', max_length=100, blank=True, null=True)
    vk = models.CharField('VK', max_length=100, blank=True, null=True)
    yandex = models.CharField(
        'Яндекс Мессенджер', max_length=100, blank=True, null=True)
    group = models.CharField('Группа', max_length=100, blank=True, null=True)
    start_english_level = models.CharField(
        'Начальный уровень английского', max_length=50, blank=True, null=True)

    payments = models.CharField(
        'Платежи', max_length=100, blank=True, null=True)
    attendance = models.CharField(
        'Посещаемость', max_length=100, blank=True, null=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        if self.phone:
            return f'{self.phone} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'
        return f'{self.yandex_id} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'
