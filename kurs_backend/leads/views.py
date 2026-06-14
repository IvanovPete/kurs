from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.conf import settings
from .models import User


def get_csrf_token(request):
    """Возвращает CSRF-токен для кросс-доменных запросов"""
    return JsonResponse({'csrfToken': get_token(request)})


@require_http_methods(["POST"])
def register_data(request):
    """Принимает данные: телефон (обязательный) и соцсети (необязательные)"""
    phone = request.POST.get('phone')

    if not phone:
        return HttpResponse('Номер телефона обязателен', status=400)

    telegram = request.POST.get('telegram', '').strip()
    vk = request.POST.get('vk', '').strip()
    yandex = request.POST.get('yandex', '').strip()
    start_english_level = request.POST.get('start_english_level', '').strip()
    age = request.POST.get('age', '').strip()

    user = User.objects.create(
        phone=phone,
        telegram=telegram if telegram else None,
        vk=vk if vk else None,
        yandex=yandex if yandex else None,
        start_english_level=start_english_level if start_english_level else None,
        age=age if age else None
    )

    return HttpResponse(f'Заявка #{user.id} успешно создана', status=201)


@csrf_exempt
@require_http_methods(["POST"])
def yandex_auth(request):
    """
    Обрабатывает вход/регистрацию через Яндекс.
    Принимает mode (login/register) и login (логин пользователя).
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    mode = data.get('mode') or request.POST.get('mode')
    login = data.get('login') or request.POST.get('login')

    if not login:
        return HttpResponse('Логин обязателен', status=400)

    # Генерируем yandex_id на основе логина (заглушка, т.к. нет реальной OAuth)
    yandex_id = f'yandex_{login}'

    if mode == 'register':
        # Проверяем, не существует ли уже такой пользователь
        if User.objects.filter(yandex_id=yandex_id).exists():
            return HttpResponse('Пользователь с таким Яндекс-аккаунтом уже зарегистрирован', status=409)

        # Создаём нового пользователя
        User.objects.create(
            yandex_id=yandex_id,
            login=login,
            free_lessons=1  # Первое занятие бесплатно
        )
        return HttpResponse('Регистрация успешна', status=201)

    elif mode == 'login':
        # Ищем существующего пользователя
        user = User.objects.filter(yandex_id=yandex_id).first()
        if not user:
            return HttpResponse('Пользователь не найден. Сначала зарегистрируйтесь.', status=404)

        return HttpResponse('Вход успешен', status=200)

    else:
        return HttpResponse('Неверный режим. Используйте login или register.', status=400)


def welcome_page(request):
    """Страница приветствия после успешного входа"""
    return render(request, 'welcome.html')


def download_first_lesson(request):
    """Скачать первый урок английского"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', 'first-lesson.docx')
    return _download_file(file_path, 'first-lesson.docx')


def download_irregular_verbs(request):
    """Скачать шпаргалку с неправильными глаголами"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', 'irregular-verbs.docx')
    return _download_file(file_path, 'irregular-verbs.docx')


def download_user_agreement(request):
    """Скачать пользовательское соглашение"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', 'Пользовательское соглашение.docx')
    return _download_file(file_path, 'Пользовательское соглашение.docx')


def download_consent(request):
    """Скачать согласие на обработку"""
    file_path = os.path.join(settings.BASE_DIR, 'documents',
                             'Согласие на обработку персональных данных.docx')
    return _download_file(file_path, 'Согласие на обработку персональных данных.docx')


def download_privacy_policy(request):
    """Скачать политику конфиденциальности"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', 'Политика конфиденциальности.docx')
    return _download_file(file_path, 'Политика конфиденциальности.docx')


def _download_file(file_path, filename):
    """Вспомогательная функция для скачивания файла"""
    if not os.path.exists(file_path):
        raise Http404('Файл не найден')

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(
        ), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
