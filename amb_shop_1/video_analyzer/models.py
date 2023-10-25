from django.db import models


# Модель для хранения информации о файлах
class UserFiles(models.Model):
    user_id = models.IntegerField(
        blank=True,
        null=True,
        default=1,
    )
    file_path = models.CharField(
        max_length=255
    )
    cookie_value = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    video_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    # created_at = models.DateTimeField(auto_now_add=True)
