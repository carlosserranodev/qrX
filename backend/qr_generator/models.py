from django.db import models

# Create your models here.

class QRCode(models.Model):
    url = models.URLField()
    file_name = models.CharField(max_length=255)
    qr_image = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
