from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from django.conf import settings
from .models import Lead


@csrf_exempt
@require_http_methods(["POST"])
def register_data(request):
    """Принимает данные: телефон (обязательный) и соцсети (необязательные)"""
    phone = request.POST.get('phone')

    if not phone:
        return HttpResponse('Номер телефона обязателен', status=400)

    # Получаем данные соцсетей (могут быть пустыми)
    telegram = request.POST.get('telegram', '').strip()
    vk = request.POST.get('vk', '').strip()
    yandex = request.POST.get('yandex', '').strip()
    start_english_level = request.POST.get('start_english_level', '').strip()
    age = request.POST.get('age', '').strip()

    # Создаем заявку
    lead = Lead.objects.create(
        phone=phone,
        telegram=telegram if telegram else None,
        vk=vk if vk else None,
        yandex=yandex if yandex else None,
        start_english_level=start_english_level if start_english_level else None,
        age=age if age else None
    )

    return HttpResponse(f'Заявка #{lead.id} успешно создана', status=201)


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
