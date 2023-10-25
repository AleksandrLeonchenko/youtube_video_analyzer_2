from celery import shared_task
from datetime import datetime, timedelta
from django.db import models
import os

from video_analyzer.models import UserFiles


@shared_task  # Декоратор, позволяющий Celery определять функцию как задачу
def clean_up_files():
    expiry_period = datetime.now() - timedelta(
        days=1)  # Вычисление времени, предшествующего 24 часам от текущего момента
    outdated_files = UserFiles.objects.filter(
        created_at__lt=expiry_period)  # Получение файлов, созданных ранее, чем заданный срок

    for file_obj in outdated_files:  # Перебор всех устаревших файлов
        file_path = file_obj.file_path  # Получение пути к файлу из объекта
        if os.path.exists(file_path):  # Проверка существования файла по указанному пути
            os.remove(file_path)  # Удаление файла по указанному пути
            file_obj.delete()  # Удаление объекта файла из базы данных
