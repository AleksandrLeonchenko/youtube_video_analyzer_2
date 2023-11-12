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
from .serializers import UploadingVideoFileSerializer, VideoFilesSerializer, ObjectLabelsSerializer
from .service import VideoProcessingService, VideoFileUploader


class UploadingVideoFile(APIView):
    """
    Класс UploadingVideoFile предоставляет API-эндпоинт для загрузки видеофайла.

    Attributes:
        parser_classes (list): Список парсеров, включая MultiPartParser, для обработки запроса.
        serializer_class (Serializer): Сериализатор для обработки данных запроса.

    Methods:
        post(request): Обработка HTTP POST-запроса на загрузку видеофайла. Использует VideoFileUploader
                       для обработки запроса и возвращает соответствующий HTTP-ответ.

    """
    parser_classes = [MultiPartParser]
    serializer_class = UploadingVideoFileSerializer

    def post(self, request):
        """
        Обрабатывает HTTP POST-запрос на загрузку видеофайла.

        Args:
            request (rest_framework.request.Request): Объект запроса.

        Returns:
            rest_framework.response.Response: HTTP-ответ с данными об успешной загрузке или ошибке.

        """
        video_file = request.FILES['video_file']
        data = request.data

        # Создаем экземпляр класса VideoFileUploader
        uploader = VideoFileUploader()

        # Вызываем метод upload_video_file
        response_data, response_status = uploader.upload_video_file(data, video_file)

        return Response(response_data, status=response_status)


class ListVideoFiles(ListAPIView):
    """
    Класс ListVideoFiles предоставляет API-эндпоинт для получения списка загруженных видеофайлов,
    предназначенных для обработки.

    Attributes:
        queryset (django.db.models.query.QuerySet): Набор данных, представляющих загруженные видеофайлы.
        serializer_class (rest_framework.serializers.Serializer): Класс сериализатора для преобразования
            объектов QuerySet в JSON-формат.

    """
    queryset = SourceVideoFiles.objects.all()
    serializer_class = VideoFilesSerializer


class DetailVideoFile(RetrieveAPIView):
    """
    Класс DetailVideoFile предоставляет API-эндпоинт для получения конкретного видеофайла из списка загруженных.

    Attributes:
        queryset (django.db.models.query.QuerySet): Набор данных, представляющих загруженные видеофайлы.
        serializer_class (rest_framework.serializers.Serializer): Класс сериализатора для преобразования
            объектов QuerySet в JSON-формат.

    """
    queryset = SourceVideoFiles.objects.all()
    serializer_class = VideoFilesSerializer


class ProcessVideo(APIView):
    """
    Класс ProcessVideo предоставляет API-эндпоинт для обработки видеофайла.

    Attributes:
        service (VideoProcessingService): Экземпляр класса VideoProcessingService для обработки видео.

    Methods:
        get(self, request, pk): Обработка GET-запроса для получения данных о конкретном видеофайле.
        post(self, request, pk: int, *args, **kwargs): Обработка POST-запроса для инициации обработки видеофайла.

    """
    # Экземпляр класса VideoProcessingService для обработки видео
    service = VideoProcessingService()

    def get(self, request, pk):
        """
        Обработка GET-запроса для получения данных о конкретном видеофайле.

        Args:
            request: Объект запроса Django.
            pk (int): Идентификатор видеофайла.

        Returns:
            Response: Объект ответа Django REST framework.

        """

        try:
            # Получение объекта SourceVideoFiles по идентификатору
            instance = SourceVideoFiles.objects.get(pk=pk)
            # Создание объекта сериализатора для преобразования данных в JSON
            serializer = VideoFilesSerializer(instance)
            print('-----get-----instance----------', instance)
            print('-----get-----serializer.data----------', serializer.data)
            # Возврат ответа с данными объекта и кодом состояния HTTP 200 (OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SourceVideoFiles.DoesNotExist:
            # Возврат ответа с сообщением об ошибке и кодом состояния HTTP 404 (NOT FOUND)
            return Response({"message": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk: int, *args, **kwargs):
        """
        Обработка POST-запроса для инициации обработки видеофайла.

        Args:
            request: Объект запроса Django.
            pk (int): Идентификатор видеофайла.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Объект ответа Django REST framework.

        """
        # Создание объекта сериализатора для преобразования данных в JSON
        serializer = ObjectLabelsSerializer(data=request.data)

        if serializer.is_valid():
            # Получение меток объектов из валидированных данных сериализатора
            object_labels = serializer.validated_data.get('object_labels')
            # Получение объекта SourceVideoFiles по идентификатору
            instance = SourceVideoFiles.objects.get(pk=pk)
            # Получение видеофайла из объекта SourceVideoFiles
            video_file = instance.video_file
            # Вызов функции process_video из сервиса для обработки видео
            self.service.process_video(video_file, object_labels)
            # Возврат ответа с сообщением об успешной инициации обработки и кодом состояния HTTP 200 (OK)
            return Response({"message": "Video processing initiated"}, status=200)
        # Возврат ответа с ошибками сериализатора и кодом состояния HTTP 400 (BAD REQUEST)
        return Response(serializer.errors, status=400)
