from django.db import models

# Create your models here.

class QRCode(models.Model):
    url = models.URLField()
    file_name = models.CharField(max_length=255)
    qr_image = models.ImageField(upload_to='qr_codes/')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)  # Nuevo campo
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
