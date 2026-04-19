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
    
    # Создаем заявку
    lead = Lead.objects.create(
        phone=phone,
        telegram=telegram if telegram else None,
        vk=vk if vk else None,
        yandex=yandex if yandex else None
    )
    
    return HttpResponse(f'Заявка #{lead.id} успешно создана', status=201)

def download_user_agreement(request):
    """Скачать пользовательское соглашение"""
    file_path = os.path.join(settings.BASE_DIR, 'documents', 'user_agreement.docx')
    return _download_file(file_path, 'user_agreement.docx')

def download_consent(request):
    """Скачать согласие на обработку"""
    file_path = os.path.join(settings.BASE_DIR, 'documents', 'consent.docx')
    return _download_file(file_path, 'consent.docx')

def download_privacy_policy(request):
    """Скачать политику конфиденциальности"""
    file_path = os.path.join(settings.BASE_DIR, 'documents', 'privacy_policy.docx')
    return _download_file(file_path, 'privacy_policy.docx')

def _download_file(file_path, filename):
    """Вспомогательная функция для скачивания файла"""
    if not os.path.exists(file_path):
        raise Http404('Файл не найден')
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response