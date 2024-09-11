import qrcode
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import QRCode
import os
import logging

logger = logging.getLogger(__name__)

class GenerateQRCodeView(APIView):
    def post(self, request):
        url = request.data.get('url')
        file_name = request.data.get('file_name')

        if not url or not file_name:
            return Response({'error': 'URL and file name are required'}, status=status.HTTP_400_BAD_REQUEST)

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure the directory exists
        qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_code_dir, exist_ok=True)
        
        file_path = os.path.join(qr_code_dir, f"{file_name}.png")
        
        logger.debug(f"Attempting to save file to: {file_path}")
        
        img.save(file_path)
        logger.debug(f"File saved successfully: {file_path}")

        qr_code = QRCode.objects.create(
            url=url,
            file_name=file_name,
            qr_image=f"qr_codes/{file_name}.png"
        )

        return Response({
            'message': 'QR Code generated successfully',
            'file_url': request.build_absolute_uri(qr_code.qr_image.url)
        }, status=status.HTTP_201_CREATED)
