from django.urls import path
from .views import GenerateQRCodeView

urlpatterns = [
    path('generate/', GenerateQRCodeView.as_view(), name='generate_qr'),
]
