import datetime

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.http import JsonResponse
import cv2
import numpy as np
import tensorflow as tf
import json
import os

from amb_shop_1 import settings
from amb_shop_1.settings import MEDIA_ROOT

from .models import ProcessedFiles, SourceVideoFiles
from .serializers import UploadingVideoFileSerializer, VideoFilesSerializer


class UploadingVideoFile(APIView):
    """
    Загрузка видеофайлов для дальнейшей обработки
    """
    parser_classes = [MultiPartParser]  # Для обработки запросов с файлами
    serializer_class = UploadingVideoFileSerializer

    def post(self, request):
        video_file = request.FILES['video_file']  # Получаем видеофайл из POST-запроса
        serializer = self.serializer_class(data=request.data)  # Создаём экземпляр сериализатора с данными запроса

        if serializer.is_valid():
            # Пытаемся получить объект или создать его, если он не существует
            instance, created = SourceVideoFiles.objects.get_or_create(
                # Если объект создается, то устанавливаются дополнительные поля
                file_name=serializer.validated_data['file_name'],
                defaults={'date_of_download': datetime.date.today(),
                          'video_file': video_file}
            )
            if created:  # Если объект был создан успешно:
                # Формируем данные для успешного ответа
                response_data = {
                    "file_name": instance.file_name,
                    "date_of_download": instance.date_of_download,
                    "id": instance.id
                }
                return Response(response_data, status=status.HTTP_200_OK)
            # Если объект уже существует:
            else:
                return Response({"message": "File already exists"}, status=status.HTTP_400_BAD_REQUEST)
        # Если данные сериализатора не являются валидными:
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListVideoFiles(ListAPIView):
    """
    Вывод списка загруженных для обработки видеофайлов
    """
    queryset = SourceVideoFiles.objects.all()
    serializer_class = VideoFilesSerializer


class DetailVideoFile(RetrieveAPIView):
    """
    Вывод конкретного видеофайла
    """
    queryset = SourceVideoFiles.objects.all()
    serializer_class = VideoFilesSerializer


class ProcessVideo1(APIView):
    """
    Здесь обрабатывается видеофайл
    """

    def detect_objects(self, frame):
        # model = tf.saved_model.load('../ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        model = tf.saved_model.load('ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели0.+-
        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)  # Преобразование кадра в тензор
        detections = infer(input_tensor)  # Применение модели к тензору для обнаружения объектов
        boxes = detections['detection_boxes'][0].numpy()  # Извлечение границ обнаруж. объектов из результатов модели
        classes = detections['detection_classes'][0].numpy().astype(np.int32)  # Извлечение классов ...
        scores = detections['detection_scores'][0].numpy()  # Извлечение оценок ...

        return boxes, classes, scores

    def process_video(self, video_file):
        print('----/////---до работы функция process_video---/////----')
        model = tf.saved_model.load('ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели
        # video_path = os.path.join(MEDIA_ROOT, "source_video_files/test.mp4")
        print('---*******1*****------video_file-----', video_file)
        # video_path = os.path.relpath(os.path.join(MEDIA_ROOT, "source_video_files/test.mp4"), settings.BASE_DIR)
        video_path = os.path.relpath(os.path.join(MEDIA_ROOT, str(video_file)), settings.BASE_DIR)
        print('---*******2*****------video_path-----', video_path)
        cap = cv2.VideoCapture(video_path)  # Инициализация объекта видеозахвата с помощью cv2.VideoCapture
        detections_data = []  # Инициализация пустого списка для обнаруженных объектов
        print('---1------detections_data-----', detections_data)
        print('---1------cap-----', cap)

        frame_count = 0  # Счетчик кадров

        while cap.isOpened():  # Цикл, работающий пока видеозахват открыт
            ret, frame = cap.read()  # Чтение кадра из видеозахвата
            if not ret:  # Проверка, если кадр не был прочитан
                break  # Выход из цикла

            if frame_count % 100 == 0:  # Проверка для каждого 100-го кадра
                print('---1------frame_count-----', frame_count)
                boxes, classes, scores = self.detect_objects(frame)  # Границы, оценки и классы обнаруженных объектов

                confidence_threshold = 0.5

                for box, score, cls in zip(boxes, scores, classes):
                    print('---1------box-----', box)
                    print('---1------score-----', score)
                    print('---1------cls-----', cls)
                    print('---2------frame_count-----', frame_count)
                    # Проверка, является ли класс объекта равным 1 и оценка больше порога:
                    if cls == 1 and score >= confidence_threshold:
                        height, width, _ = frame.shape
                        ymin, xmin, ymax, xmax = box
                        ymin = int(ymin * height)
                        xmin = int(xmin * width)
                        ymax = int(ymax * height)
                        xmax = int(xmax * width)
                        print('---1------ymin, xmin, ymax, xmax-----', ymin, xmin, ymax, xmax)

                        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Получение времени в секундах
                        print('---1------timestamp-----', timestamp)

                        # Нарисуем прямоугольник вокруг объекта на кадре
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        detections_data.append({
                            "coordinates": [xmin, ymin, xmax, ymax],  # Координаты границ объекта
                            "confidence": float(score),  # Оценка объекта
                            "timestamp": timestamp  # Временная метка объекта
                        })
                        print('---2------detections_data-----', detections_data)

                # Получение имени исходного видеофайла
                video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
                # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
                json_file_name = f"{video_name}_detections.json"
                with open(json_file_name, "w") as f:
                    json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON

            frame_count += 1  # Увеличение счетчика кадров

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Проверка, была ли нажата клавиша "q" для выхода
                break  # Прерывание цикла обработки кадров

        cap.release()  # Освобождение захваченного видеопотока после обработки видео
        cv2.destroyAllWindows()  # Закрытие всех окон, созданных OpenCV
        print('----/////---после работы функция process_video---/////----')
        pass

    def get(self, request, pk):
        try:
            instance = SourceVideoFiles.objects.get(pk=pk)
            video_file = instance.video_file
            print('----до работы функции process_video---instance----', instance.file_name, instance.id,
                  instance.video_file)
            self.process_video(video_file)
            return Response({"message": "Video processing initiated"}, status=status.HTTP_200_OK)
        except SourceVideoFiles.DoesNotExist:
            return Response({"message": "Video not found"}, status=status.HTTP_404_NOT_FOUND)


class ProcessVideo(APIView):
    """
    Здесь обрабатывается видеофайл
    """
    detections_data = []  # Инициализация пустого списка для обнаруженных объектов

    def detect_objects(self, frame):
        # model = tf.saved_model.load('../ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        model = tf.saved_model.load('ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели0.+-
        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)  # Преобразование кадра в тензор
        detections = infer(input_tensor)  # Применение модели к тензору для обнаружения объектов
        boxes = detections['detection_boxes'][0].numpy()  # Извлечение границ обнаруж. объектов из результатов модели
        classes = detections['detection_classes'][0].numpy().astype(np.int32)  # Извлечение классов ...
        scores = detections['detection_scores'][0].numpy()  # Извлечение оценок ...

        return boxes, classes, scores

    def process_video(self, video_file):
        print('----/////---до работы функция process_video---/////----')
        print('---*******1*****------video_file-----', video_file)
        model = tf.saved_model.load('ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели
        # video_path = os.path.join(MEDIA_ROOT, "source_video_files/test.mp4")
        # video_path = os.path.relpath(os.path.join(MEDIA_ROOT, "source_video_files/test.mp4"), settings.BASE_DIR)
        video_path = os.path.relpath(os.path.join(MEDIA_ROOT, str(video_file)), settings.BASE_DIR)
        print('---*******2*****------video_path-----', video_path)
        cap = cv2.VideoCapture(video_path)  # Инициализация объекта видеозахвата с помощью cv2.VideoCapture
        # detections_data = []  # Инициализация пустого списка для обнаруженных объектов
        print('---1------detections_data-----', self.detections_data)
        print('---1------cap-----', cap)
        self.detections_data = ['test 123']  # Инициализация тестового списка обнаруженных объектов

        # frame_count = 0  # Счетчик кадров
        #
        # while cap.isOpened():  # Цикл, работающий пока видеозахват открыт
        #     ret, frame = cap.read()  # Чтение кадра из видеозахвата
        #     if not ret:  # Проверка, если кадр не был прочитан
        #         break  # Выход из цикла
        #
        #     if frame_count % 100 == 0:  # Проверка для каждого 100-го кадра
        #         print('---1------frame_count-----', frame_count)
        #         boxes, classes, scores = self.detect_objects(frame)  # Границы, оценки и классы обнаруженных объектов
        #
        #         confidence_threshold = 0.5
        #
        #         for box, score, cls in zip(boxes, scores, classes):
        #             print('---1------box-----', box)
        #             print('---1------score-----', score)
        #             print('---1------cls-----', cls)
        #             print('---2------frame_count-----', frame_count)
        #             # Проверка, является ли класс объекта равным 1 и оценка больше порога:
        #             if cls == 1 and score >= confidence_threshold:
        #                 height, width, _ = frame.shape
        #                 ymin, xmin, ymax, xmax = box
        #                 ymin = int(ymin * height)
        #                 xmin = int(xmin * width)
        #                 ymax = int(ymax * height)
        #                 xmax = int(xmax * width)
        #                 print('---1------ymin, xmin, ymax, xmax-----', ymin, xmin, ymax, xmax)
        #
        #                 timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Получение времени в секундах
        #                 print('---1------timestamp-----', timestamp)
        #
        #                 # Нарисуем прямоугольник вокруг объекта на кадре
        #                 cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        #                 self.detections_data.append({
        #                     "coordinates": [xmin, ymin, xmax, ymax],  # Координаты границ объекта
        #                     "confidence": float(score),  # Оценка объекта
        #                     "timestamp": timestamp  # Временная метка объекта
        #                 })
        #                 print('---2------detections_data-----', self.detections_data)
        #
        #
        #         # # Получение имени исходного видеофайла
        #         # video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
        #         # # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
        #         # json_file_name = f"{video_name}_detections.json"
        #         # with open(json_file_name, "w") as f:
        #         #     json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON
        #
        #     frame_count += 1  # Увеличение счетчика кадров
        #
        #     if cv2.waitKey(1) & 0xFF == ord('q'):  # Проверка, была ли нажата клавиша "q" для выхода
        #         break  # Прерывание цикла обработки кадров
        #
        #     # # Получение имени исходного видеофайла
        #     # video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
        #     # # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
        #     # json_file_name = f"{video_name}_detections.json"
        #     # with open(json_file_name, "w") as f:
        #     #     json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON
        #
        # cap.release()  # Освобождение захваченного видеопотока после обработки видео
        # cv2.destroyAllWindows()  # Закрытие всех окон, созданных OpenCV

        print('----/////---после работы функция process_video---/////----')

        # Получение имени исходного видеофайла
        video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
        # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
        json_file_name = f"{video_name}_detections.json"
        # Путь сохранения json-файла
        # file_path = f"media/processed_files/{json_file_name}"  # Тоже допустимый вариант
        file_path = os.path.relpath(os.path.join(MEDIA_ROOT, "processed_files", json_file_name), settings.BASE_DIR)

        # with open(json_file_name, "w") as f:
        with open(file_path, "w") as f:
            json.dump(self.detections_data, f)  # Запись обнаруженных данных в формате JSON по пути file_path

        print('---13------video_path-----', video_path)
        print('---13------file_name-----', json_file_name)
        print('---13------file_path-----', file_path)
        print('---13------processing_data_file-----', self.detections_data)
        print('---13------f-----', f)
        # Заполняем поля в модели ProcessedFiles:
        if self.detections_data:
            # Пытаемся получить объект или создать его, если он не существует
            instance, created = ProcessedFiles.objects.get_or_create(
                # Если объект создается, то устанавливаются дополнительные поля
                file_name=json_file_name,
                file_path=file_path,
                processing_data_file=self.detections_data,
                defaults={'date_of_creation': datetime.date.today(),
                          'processing_data_file': self.detections_data}
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

    def get(self, request, pk):
        try:
            instance = SourceVideoFiles.objects.get(pk=pk)
            video_file = instance.video_file
            print('---***get***----до работы функции process_video-------')
            # self.process_video(video_file)
            print('---23------self.process_video(video_file)-----', self.process_video(video_file))
            print('---***get***----после работы функции process_video-------')

            return Response({"message": "Video processing initiated"}, status=status.HTTP_200_OK)
        except SourceVideoFiles.DoesNotExist:
            return Response({"message": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
