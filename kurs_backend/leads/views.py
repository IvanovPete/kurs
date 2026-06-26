from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.contrib.auth.hashers import make_password, check_password
import os
import json
import urllib.request
import urllib.parse
import logging
from django.conf import settings
from .models import User

logger = logging.getLogger(__name__)

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


@require_http_methods(["POST"])
def register_phone(request):
    """Регистрация по номеру телефона и паролю"""
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        data = {}

    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    if not phone:
        return JsonResponse({'error': 'Номер телефона обязателен'}, status=400)
    if not password or len(password) < 4:
        return JsonResponse({'error': 'Пароль должен быть не менее 4 символов'}, status=400)

    if User.objects.filter(phone=phone).exists():
        return JsonResponse({'error': 'Этот номер телефона уже зарегистрирован'}, status=409)

    user = User.objects.create(
        phone=phone,
        password=make_password(password),
        free_lessons=1,
    )

    request.session['user_phone'] = phone
    request.session['user_name'] = phone

    return JsonResponse({
        'ok': True,
        'user_id': user.id,
        'phone': phone,
    }, status=201)


@require_http_methods(["POST"])
def login_phone(request):
    """Вход по номеру телефона и паролю"""
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        data = {}

    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    if not phone or not password:
        return JsonResponse({'error': 'Телефон и пароль обязательны'}, status=400)

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь с таким номером не найден'}, status=404)

    if not user.password:
        return JsonResponse({'error': 'Этот аккаунт зарегистрирован через Яндекс. Используйте вход через Яндекс.'}, status=401)

    if not check_password(password, user.password):
        return JsonResponse({'error': 'Неверный пароль'}, status=401)

    request.session['user_phone'] = phone
    request.session['user_name'] = user.first_name or phone
    request.session['user_id'] = user.id

    return JsonResponse({
        'ok': True,
        'phone': phone,
        'name': user.first_name or phone,
    })


@require_http_methods(["POST"])
def logout_user(request):
    """Выход из аккаунта"""
    request.session.flush()
    return JsonResponse({'ok': True})


def yandex_auth(request):
    """
    Редиректит пользователя на страницу авторизации Яндекса.
    """
    try:
        mode = request.GET.get('mode', 'login')
        # Передаём mode через state (Яндекс не поддерживает кастомные query параметры в redirect_uri)
        state = 'mode=' + mode

        params = urllib.parse.urlencode({
            'client_id': YANDEX_CLIENT_ID,
            'redirect_uri': YANDEX_REDIRECT_URI,
            'response_type': 'code',
            'state': state,
            'force_confirm': 1,  # Всегда показывать окно подтверждения Яндекса
        })
        yandex_url = 'https://oauth.yandex.ru/authorize?' + params
        return redirect(yandex_url)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('YANDEX_AUTH_ERROR')
        return HttpResponse('Ошибка: ' + str(e), status=500)


def yandex_callback(request):
    """
    Обрабатывает callback от Яндекса после авторизации пользователя.
    """
    try:
        code = request.GET.get('code')
        state = request.GET.get('state', '')
        error = request.GET.get('error')

        # Извлекаем mode из state (формат: 'mode=login' или 'mode=register')
        mode = 'login'
        if state.startswith('mode='):
            mode = state.split('mode=', 1)[1]

        if error or not code:
            return HttpResponse('Авторизация отменена или произошла ошибка', status=400)

        # 1. Обмениваем код на токен
        token_data = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': YANDEX_CLIENT_ID,
            'client_secret': YANDEX_CLIENT_SECRET,
            'redirect_uri': YANDEX_REDIRECT_URI,
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
            logger.exception('YANDEX_TOKEN_ERROR')
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
            logger.exception('YANDEX_USERINFO_ERROR')
            return HttpResponse('Ошибка получения данных пользователя: ' + str(e), status=400)

        yandex_id = user_info.get('id', '')
        login = user_info.get('login', '')
        email = user_info.get('default_email', '')
        first_name = user_info.get('first_name', '')
        last_name = user_info.get('last_name', '')
        sex = user_info.get('sex', '')
        birthday = user_info.get('birthday', '')
        phone = user_info.get('default_phone', {}).get('number', '') if isinstance(
            user_info.get('default_phone'), dict) else ''
        avatar_url = ''
        if user_info.get('is_avatar_empty', True) == False and user_info.get('default_avatar_id'):
            avatar_url = 'https://avatars.yandex.net/get-yapic/' + \
                user_info.get('default_avatar_id', '') + '/islands-200'

        if not yandex_id:
            return HttpResponse('Не удалось получить ID пользователя', status=400)

        # 3. Создаём или находим пользователя
        user, created = User.objects.get_or_create(
            yandex_id=yandex_id,
            defaults={
                'login': login,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'sex': sex,
                'birthday': birthday,
                'phone': phone,
                'avatar_url': avatar_url,
                'free_lessons': 1,
            }
        )

        if not created:
            user.login = login
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.sex = sex
            user.birthday = birthday
            if phone:
                user.phone = phone
            if avatar_url:
                user.avatar_url = avatar_url
            user.save()

        # 4. Сохраняем данные в сессии
        request.session['yandex_user_id'] = yandex_id
        request.session['user_login'] = login
        request.session['user_phone'] = phone
        request.session['user_name'] = first_name + ' ' + last_name

        # 5. Редиректим на welcome.html
        frontend_url = 'https://kurs.zapto.org/welcome.html'
        return redirect(frontend_url)
    except Exception as e:
        logger.exception('YANDEX_CALLBACK_CRITICAL_ERROR')
        return HttpResponse('Внутренняя ошибка сервера: ' + str(e), status=500)


def get_user_info(request):
    """Возвращает информацию о текущем пользователе по сессии"""
    # Сначала проверяем вход через Яндекс
    yandex_id = request.session.get('yandex_user_id')
    if yandex_id:
        user = User.objects.filter(yandex_id=yandex_id).first()
        if user:
            return JsonResponse({
                'authenticated': True,
                'login': user.login or '',
                'name': (user.first_name or '') + ' ' + (user.last_name or ''),
                'email': user.email or '',
                'phone': user.phone or '',
                'avatar_url': user.avatar_url or '',
            })

    # Проверяем вход по телефону
    phone = request.session.get('user_phone')
    if phone:
        user = User.objects.filter(phone=phone).first()
        if user:
            return JsonResponse({
                'authenticated': True,
                'phone': user.phone or '',
                'name': user.first_name or user.phone or '',
            })

    return JsonResponse({'authenticated': False})


@require_http_methods(["POST"])
def save_phone(request):
    """Сохраняет номер телефона после входа"""
    yandex_id = request.session.get('yandex_user_id')
    if not yandex_id:
        return JsonResponse({'error': 'Не авторизован'}, status=401)

    import json
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        data = {}

    phone = data.get('phone', '') or request.POST.get('phone', '')
    phone = phone.strip()

    if not phone:
        return JsonResponse({'error': 'Номер телефона обязателен'}, status=400)

    user = User.objects.filter(yandex_id=yandex_id).first()
    if not user:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)

    user.phone = phone
    user.save()
    request.session['user_phone'] = phone
    return JsonResponse({'ok': True}, status=200)


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
