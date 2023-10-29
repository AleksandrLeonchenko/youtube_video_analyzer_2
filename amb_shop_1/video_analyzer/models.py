from django.db import models


# Модель для хранения информации о файлах
class UserFiles(models.Model):
    user_id = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        verbose_name='ID пользователя'
    )
    file_path = models.CharField(
        max_length=1000,
        verbose_name='Путь к файлу с данными'
    )
    cookie_value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='cookie пользователя'
    )
    video_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Идентификатор видео'
    )
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP пользователя'
    )
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_path

    class Meta:
        verbose_name = 'Клиентский файл'
        verbose_name_plural = 'Клиентские файлы'
        ordering = ['id']
