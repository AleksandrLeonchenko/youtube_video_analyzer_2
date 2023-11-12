from django.db import models


class ProcessedFiles(models.Model):
    file_name = models.CharField(
        max_length=1000,
        default='123',
        verbose_name='Имя файла',
    )
    processing_data_file = models.JSONField(
        default=dict,
        verbose_name='Файл с данными обработки'
    )
    file_path = models.CharField(
        max_length=1000,
        null=True,
        verbose_name='Путь к файлу с данными'
    )
    date_of_creation = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='Дата создания файла с данными'
    )

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = 'Файл с данными обработки админом видеофайлов'
        verbose_name_plural = 'Файлы с данными обработки админом видеофайлов'
        ordering = ['id']


class SourceVideoFiles(models.Model):
    file_name = models.CharField(
        max_length=1000,
        null=True,  # Нужно это поле сделать обязательным
        verbose_name='Имя исходного видеофайла'
    )
    video_file = models.FileField(
        # upload_to="media/source_video_files",
        upload_to="source_video_files",
        null=True,
        verbose_name='Исходный видеофайл'
    )
    date_of_download = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='Дата загрузки видеофайла'
    )
    processed = models.BooleanField(
        default=False,
        verbose_name='Видеофайл обработан'
    )

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = 'Исходный видеофайл для обработки админом'
        verbose_name_plural = 'Исходные видеофайлы для обработки админом'
        ordering = ['id']


class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    video_file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
