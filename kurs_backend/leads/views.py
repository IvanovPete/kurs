from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import os
import json
import urllib.request
import urllib.parse
from django.conf import settings
from .models import User


YANDEX_CLIENT_ID = os.environ.get('YANDEX_CLIENT_ID', '')
YANDEX_CLIENT_SECRET = os.environ.get('YANDEX_CLIENT_SECRET', '')
YANDEX_REDIRECT_URI = os.environ.get(
    'YANDEX_REDIRECT_URI', 'http://localhost:8000/api/yandex/callback/')


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


def yandex_auth(request):
    """
    Редиректит пользователя на страницу авторизации Яндекса.
    Принимает параметр ?mode=login или ?mode=register (опционально).
    """
    mode = request.GET.get('mode', 'login')
    callback_url = YANDEX_REDIRECT_URI + '?mode=' + mode

    params = urllib.parse.urlencode({
        'client_id': YANDEX_CLIENT_ID,
        'redirect_uri': callback_url,
        'response_type': 'code',
    })
    yandex_url = 'https://oauth.yandex.ru/authorize?' + params
    return redirect(yandex_url)


def yandex_callback(request):
    """
    Обрабатывает callback от Яндекса после авторизации пользователя.
    """
    code = request.GET.get('code')
    mode = request.GET.get('mode', 'login')
    error = request.GET.get('error')

    if error or not code:
        return HttpResponse('Авторизация отменена или произошла ошибка', status=400)

    # 1. Обмениваем код на токен
    callback_url = YANDEX_REDIRECT_URI + '?mode=' + mode
    token_data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': YANDEX_CLIENT_ID,
        'client_secret': YANDEX_CLIENT_SECRET,
        'redirect_uri': callback_url,
    }).encode()

    token_req = urllib.request.Request(
        'https://oauth.yandex.ru/token',
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    try:
        token_resp = urllib.request.urlopen(token_req)
        token_json = json.loads(token_resp.read())
        access_token = token_json.get('access_token')
    except Exception as e:
        return HttpResponse('Ошибка получения токена: ' + str(e), status=400)

    if not access_token:
        return HttpResponse('Не удалось получить токен', status=400)

    # 2. Получаем информацию о пользователе
    user_req = urllib.request.Request(
        'https://login.yandex.ru/info',
        headers={'Authorization': 'OAuth ' + access_token}
    )

    try:
        user_resp = urllib.request.urlopen(user_req)
        user_info = json.loads(user_resp.read())
    except Exception as e:
        return HttpResponse('Ошибка получения данных пользователя: ' + str(e), status=400)

    yandex_id = user_info.get('id', '')
    login = user_info.get('login', '')
    email = user_info.get('default_email', '')

    if not yandex_id:
        return HttpResponse('Не удалось получить ID пользователя', status=400)

    # 3. Создаём или находим пользователя
    user, created = User.objects.get_or_create(
        yandex_id=yandex_id,
        defaults={
            'login': login,
            'email': email,
            'free_lessons': 1,
        }
    )

    if not created:
        # Обновляем данные при каждом входе
        user.login = login
        user.email = email
        user.save()

    # 4. Сохраняем yandex_id в сессии
    request.session['yandex_user_id'] = yandex_id
    request.session['user_login'] = login

    # 5. Редиректим на welcome.html
    frontend_url = 'https://kurs.zapto.org/welcome.html'
    return redirect(frontend_url)


def download_first_lesson(request):
    """Скачать первый урок английского"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', 'Первый урок английского языка.docx')
    return _download_file(file_path, 'Первый урок английского языка.docx')


def download_irregular_verbs(request):
    """Скачать шпаргалку с неправильными глаголами"""
    file_path = os.path.join(
        settings.BASE_DIR, 'documents', '30 самых важных неправильных глаголов.docx')
    return _download_file(file_path, '30 самых важных неправильных глаголов.docx')


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
