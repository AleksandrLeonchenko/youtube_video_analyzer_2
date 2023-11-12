import datetime
import cv2
import numpy as np
import tensorflow as tf
import json
import os

from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from amb_shop_1 import settings
from amb_shop_1.settings import MEDIA_ROOT
from .models import ProcessedFiles, SourceVideoFiles
from .serializers import UploadingVideoFileSerializer, ObjectLabelsSerializer


class VideoFileUploader:
    """
    Класс VideoFileUploader предоставляет метод для обработки запроса на загрузку видеофайла.

    Methods:
        upload_video_file(data, video_file): Обрабатывает запрос на загрузку видеофайла.
            Создает объект UploadingVideoFileSerializer для обработки данных запроса.
            Проверяет валидность данных сериализатора и выполняет загрузку или создание объекта SourceVideoFiles.
            Если объект успешно создан, возвращает данные об объекте и HTTP-статус 200 (OK).
            Если объект уже существует, возвращает сообщение об ошибке и HTTP-статус 400 (BAD REQUEST).
            Если данные сериализатора не валидны, возвращает ошибки сериализатора и HTTP-статус 400 (BAD REQUEST).

    """

    @staticmethod
    def upload_video_file(data, video_file):
        """
        Метод upload_video_file обрабатывает запрос на загрузку видеофайла.
        Создается экземпляр сериализатора UploadingVideoFileSerializer для обработки данных запроса.
        Проверяется валидность данных сериализатора с использованием serializer.is_valid().
        Если данные валидны, выполняется попытка получения или создания объекта SourceVideoFiles в базе данных.
        При создании устанавливаются дополнительные поля, такие как date_of_download и video_file.
        Если объект был успешно создан, формируется словарь response_data с данными об объекте (имя файла,
        дата загрузки и идентификатор).
        Возвращается сформированный словарь вместе с кодом состояния HTTP 200 (OK).
        Если объект уже существует, возвращается сообщение об ошибке и код состояния HTTP 400 (BAD REQUEST).
        Если данные сериализатора не являются валидными, возвращаются ошибки сериализатора и
        код состояния HTTP 400 (BAD REQUEST).

        Args:
            data (dict): Данные запроса, представленные в виде словаря.
            video_file (django.core.files.uploadedfile.InMemoryUploadedFile): Загруженный видеофайл.

        Returns:
            tuple: Кортеж, содержащий:
                - dict: Словарь с данными об объекте, если объект успешно создан.
                - int: Код состояния HTTP.

        Raises:
            serializers.ValidationError: Если данные сериализатора не являются валидными.
        """
        # Создаем экземпляр сериализатора для обработки данных запроса
        serializer = UploadingVideoFileSerializer(data=data)

        # Проверяем валидность данных сериализатора
        if serializer.is_valid():
            # Получаем или создаем объект SourceVideoFiles
            instance, created = SourceVideoFiles.objects.get_or_create(
                file_name=serializer.validated_data['file_name'],
                defaults={'date_of_download': datetime.date.today(),
                          'video_file': video_file}
            )

            # Если объект был создан, формируем данные для успешного ответа
            if created:
                response_data = {
                    "file_name": instance.file_name,
                    "date_of_download": instance.date_of_download,
                    "id": instance.id
                }
                return response_data, status.HTTP_200_OK
            # Если объект уже существует, возвращаем сообщение об ошибке
            else:
                return {"message": "File already exists"}, status.HTTP_400_BAD_REQUEST
        # Если данные сериализатора не являются валидными, возвращаем ошибку
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST


class VideoProcessingService:
    """
    Сервис для обработки видеофайлов, обнаружения объектов, и создания соответствующих JSON-файлов
    и записей в базе данных.

    Attributes:
        model: Модель обнаружения объектов, используемая сервисом.

    Methods:
        __init__: Инициализирует экземпляр класса, загружает модель при создании.
        load_model: Загружает предварительно обученную модель обнаружения объектов.
        detect_objects: Обнаруживает объекты на видеокадре.
        process_video: Обрабатывает видеофайл, обнаруживает объекты, создает JSON-файл и запись в базу данных.
    """
    model = None  # Переменная для хранения модели обнаружения объектов

    def __init__(self):
        """
        Инициализация сервиса, загрузка модели при создании экземпляра.
        """
        self.load_model()

    def load_model(self):
        """
        Инициализация сервиса, загрузка модели при создании экземпляра.
        """
        self.model = tf.saved_model.load('ssd_mobilenet_v2_coco_2018_03_29/saved_model')

    def detect_objects(self, frame):
        """
        Обнаружение объектов на видеокадре.

        Args:
            frame: Кадр видео.

        Returns:
            Кортеж из трех элементов: boxes - координаты рамок объектов,
            classes - классы объектов, scores - уверенность в обнаружении объектов.
        """
        infer = self.model.signatures["serving_default"]
        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)
        detections = infer(input_tensor)
        boxes = detections['detection_boxes'][0].numpy()
        classes = detections['detection_classes'][0].numpy().astype(np.int32)
        scores = detections['detection_scores'][0].numpy()
        return boxes, classes, scores

    def process_video(self, video_file, object_labels):
        """
        Обработка видеофайла, обнаружение объектов, создание JSON-файла и запись в базу данных.

        Args:
            video_file: Файл видео.
            object_labels: Словарь меток объектов.

        Returns:
            Ответ в виде словаря с данными о созданном файле и статусом HTTP.
        """
        detections_data = []  # Список для хранения обнаруженных объектов
        model = self.model  # Обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели
        video_path = os.path.relpath(os.path.join(MEDIA_ROOT, str(video_file)), settings.BASE_DIR)
        cap = cv2.VideoCapture(video_path)  # Инициализация объекта видеозахвата с помощью cv2.VideoCapture
        # detections_data = []  # Инициализация пустого списка для обнаруженных объектов
        print('---*******process_video*****------video_file-----', video_file)
        print('---*******process_video*****------video_path-----', video_path)
        print('---*******process_video*****-----object_labels----------', object_labels)
        print('---*******process_video*****-----self.detections_data----------', detections_data)
        print('---*******process_video*****-----detections_data-----', detections_data)
        print('---*******process_video*****----cap-----', cap)
        # self.detections_data = ['test 123']  # ТЕСТОВЫЙ СПИСОК обнаруженных объектов - для настройки

        # Поля, определяемое логикой, которую нужно будет прописать после добавления продуктов:
        # article_fragment - часть артикула продукта (или полный артикул), по которой найдём нужный продукт в БД
        # additional_identifier - дополнительный идентификатор, который затем добавим к продукту для последующей логики
        article_fragment = "123"
        additional_identifier = "456"

        frame_count = 0  # Счетчик кадров

        while cap.isOpened():  # Цикл, работающий пока видеозахват открыт
            ret, frame = cap.read()  # Чтение кадра из видеозахвата
            if not ret:  # Проверка, если кадр не был прочитан
                print('//---process_video------кадр не был прочитан-----//')
                break  # Выход из цикла

            if frame_count % 100 == 0:  # Проверка для каждого 100-го кадра
                print('---if frame_count % 100 == 0------frame_count-----', frame_count)
                boxes, classes, scores = self.detect_objects(frame)

                confidence_threshold = 0.5

                for box, score, cls in zip(boxes, scores, classes):
                    print('---for box, score, cls------box, score, cls-----', box, score, cls)

                    # Проверка, является ли класс объекта равным 1 и оценка больше порога:
                    # if cls == 1 and score >= confidence_threshold:
                    # if cls in self.object_labels and object_labels[cls] == 'person' and score >= confidence_threshold:
                    if str(cls) in object_labels and score >= confidence_threshold:
                        print('//---if cls in object_labels---//')
                        height, width, _ = frame.shape
                        ymin, xmin, ymax, xmax = box
                        ymin = int(ymin * height)
                        xmin = int(xmin * width)
                        ymax = int(ymax * height)
                        xmax = int(xmax * width)

                        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Получение времени в секундах
                        print('---1------ymin, xmin, ymax, xmax, timestamp-----', ymin, xmin, ymax, xmax, timestamp)

                        # Нарисуем прямоугольник вокруг объекта на кадре (попробовать закомментировать)
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        detections_data.append({
                            "coordinates": [xmin, ymin, xmax, ymax],  # Координаты границ объекта
                            "confidence": float(score),  # Оценка объекта
                            "timestamp": timestamp,  # Временная метка объекта
                            "item_name": object_labels[str(cls)],  # Тип объекта из коллекции объектов в object_labels
                            "article_fragment": article_fragment,  # часть артикула продукта
                            "additional_identifier": additional_identifier,  # дополнительный идентификатор
                            "frame_number": frame_count  # Номер кадра

                        })
                        print('---2------detections_data-----', detections_data)

            frame_count += 1  # Увеличение счетчика кадров

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Проверка, была ли нажата клавиша "q" для выхода
                break  # Прерывание цикла обработки кадров

        cap.release()  # Освобождение захваченного видеопотока после обработки видео
        cv2.destroyAllWindows()  # Закрытие всех окон, созданных OpenCV

        # # СОЗДАНИЕ ФАЙЛА:
        # Получение имени исходного видеофайла
        video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
        # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
        json_file_name = f"{video_name}_detections.json"
        # Путь сохранения json-файла
        # file_path = f"media/processed_files/{json_file_name}"  # Тоже допустимый вариант
        file_path = os.path.relpath(os.path.join(MEDIA_ROOT, "processed_files", json_file_name), settings.BASE_DIR)

        # with open(json_file_name, "w") as f:
        with open(file_path, "w") as f:
            json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON по пути file_path

        # # СОЗДАНИЕ ЗАПИСИ В ТАБЛИЦЕ БАЗЫ ДАННЫХ:
        print('---ТАБЛИЦA БАЗЫ ДАННЫХ------video_path-----', video_path)
        print('---ТАБЛИЦA БАЗЫ ДАННЫХ------file_name-----', json_file_name)
        print('---ТАБЛИЦA БАЗЫ ДАННЫХ------file_path-----', file_path)
        print('---ТАБЛИЦA БАЗЫ ДАННЫХ------processing_data_file-----', detections_data)
        # Заполняем поля в модели ProcessedFiles:
        if detections_data:
            # Пытаемся получить объект или создать его, если он не существует
            instance, created = ProcessedFiles.objects.get_or_create(
                # Если объект создается, то устанавливаются дополнительные поля
                file_name=json_file_name,
                file_path=file_path,
                processing_data_file=detections_data,
                defaults={'date_of_creation': datetime.date.today(),
                          'processing_data_file': detections_data}
            )
            if created:  # Если объект был создан успешно:
                # Формируем данные для успешного ответа
                response_data = {
                    "file_name": instance.file_name,
                    "date_of_creation": instance.date_of_creation,
                    "id": instance.id
                }
                return Response(response_data, status=status.HTTP_200_OK)
            # Если объект уже существует:
            else:
                return Response({"message": "File already exists"}, status=status.HTTP_400_BAD_REQUEST)
