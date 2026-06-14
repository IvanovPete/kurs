from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('api/register/', views.register_data, name='register_data'),
    path('api/csrf/', views.get_csrf_token, name='get_csrf'),
    path('api/yandex-auth/', views.yandex_auth, name='yandex_auth'),
    path('docs/user-agreement/', views.download_user_agreement, name='user_agreement'),
    path('docs/consent/', views.download_consent, name='consent'),
    path('docs/privacy-policy/', views.download_privacy_policy, name='privacy_policy'),
    path('docs/first-lesson/', views.download_first_lesson, name='first_lesson'),
    path('docs/irregular-verbs/', views.download_irregular_verbs, name='irregular_verbs'),
]