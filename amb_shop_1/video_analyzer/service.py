import os
import glob
import time

from celery import shared_task


@shared_task
def clean_up_files(user_id):  # Для удаления файла через 24 часа
    # Путь к директории, где хранятся файлы пользователя
    user_directory = f"media/{user_id}"

    # Удаление файлов, если они старше 24 часов
    for file_path in glob.glob(os.path.join(user_directory, '*')):  # Итерация по всем файлам в директории пользователя
        file_creation_time = os.path.getctime(file_path)  # Получение времени создания файла
        current_time = time.time()  # Получение текущего времени
        if current_time - file_creation_time >= 24 * 3600:  # Проверка, превышает ли возраст файла 24 часа
            if os.path.exists(file_path):  # Добавлена проверка существования файла
                os.remove(file_path)  # Удаление файла
