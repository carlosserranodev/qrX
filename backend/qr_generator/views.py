import qrcode
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import QRCode
import os
import logging
from PIL import Image, ImageDraw, ImageOps
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

logger = logging.getLogger(__name__)

def add_rounded_corners(image, radius):
    """Add rounded corners to an image."""
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255)
    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)
    return rounded_image

class GenerateQRCodeView(APIView):
    def post(self, request):
        url = request.data.get('url')
        file_name = request.data.get('file_name')
        logo = request.FILES.get('logo')

        if not url or not file_name:
            return Response({'error': 'URL and file name are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create QR code with high error correction and larger box size
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR image with rounded modules
        qr_image = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()).convert('RGBA')
        qr_image = add_rounded_corners(qr_image, radius=20)  # Add rounded corners to the QR code

        if logo:
            # Create logo image
            logo_image = Image.open(logo)
            qr_size = qr_image.size[0]  # Get the size of the QR code image
            logo_size = int(qr_size * 0.25)  # Logo will occupy approximately 25% of the QR code
            logo_image = logo_image.resize((logo_size, logo_size), Image.LANCZOS)
            logo_image = add_rounded_corners(logo_image, radius=20)  # Add rounded corners to the logo
            
            # Calculate position to center the logo
            pos = ((qr_image.size[0] - logo_image.size[0]) // 2, (qr_image.size[1] - logo_image.size[1]) // 2)
            qr_image.paste(logo_image, pos, logo_image)

        # Ensure the directory exists
        qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_code_dir, exist_ok=True)

        file_path = os.path.join(qr_code_dir, f"{file_name}.png")

        logger.debug(f"Attempting to save file to: {file_path}")

        # Save the image with high quality
        qr_image.save(file_path, 'PNG', quality=95)
        logger.debug(f"File saved successfully: {file_path}")

        # Store information in the database
        qr_code = QRCode.objects.create(
            url=url,
            file_name=file_name,
            qr_image=f"qr_codes/{file_name}.png"
        )

        return Response({
            'message': 'QR Code generated successfully',
            'file_url': request.build_absolute_uri(qr_code.qr_image.url)
        }, status=status.HTTP_201_CREATED)
