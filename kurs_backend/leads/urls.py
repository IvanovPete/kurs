from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('api/register/', views.register_data, name='register_data'),
    path('docs/user-agreement/', views.download_user_agreement, name='user_agreement'),
    path('docs/consent/', views.download_consent, name='consent'),
    path('docs/privacy-policy/', views.download_privacy_policy, name='privacy_policy'),
]