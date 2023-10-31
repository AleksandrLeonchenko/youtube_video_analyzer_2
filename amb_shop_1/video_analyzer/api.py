import json
import os
import celery

from datetime import datetime
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from celery import shared_task

from video_analyzer.models import UserFiles
from video_analyzer.serializers import UserFilesSerializer
from video_analyzer.service import clean_up_files
from amb_shop_1.settings import MEDIA_ROOT
from amb_shop_1 import settings


class ClickHandler(APIView):
    """
    Здесь принимаем POST-запрос от клиента, сохраняем нужные данные в базу,
    в частности user_id (если он есть), user_ip (ip-адрес клиента), video_id (идентификатор видео),
    file_path (путь, по которому сохраняется файл в папку media), cookie_value (куки, если они будут нужны).
    Затем по этим данным из базы можно будет найти файл. В названии файла отражены user_id, user_ip, video_id.
    В файле данные представлены в виде списка словарей, при каждом новом POST-запросе от клиента, если имя файла
    то же (user_id, user_ip, video_id те же) - то в список добавляется ещё один словарь с координатами клика,
    таймингом клика и идентификатором видео.
    Здесь файлы сохраняются не в базу, а в файловое хранилище - это для того, стобы долго их не хранить и с помощью
    селери и редис периодически удалять, так как у каждого юзера их может быть очень много.
    """
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        user_ip = request.META.get('REMOTE_ADDR')
        video_id = request.data.get('video_id')
        file_path = f"media/client_files/{user_id}_{user_ip}_{request.data.get('videoId')}.json"  # Путь для сохранения файла (1 вариант)
        # file_path = os.path.relpath(  # Путь для сохранения файла (2 вариант - не работает)
        #     os.path.join(
        #         MEDIA_ROOT,
        #         "client_files",
        #         user_id,
        #         "_",
        #         user_ip,
        #         "_",
        #         request.data.get('videoId'),
        #         ".json"
        #     ),
        #     settings.BASE_DIR
        # )

        data = request.data
        cookie_value = request.COOKIES.get('cookie_name')
        print('------request.data-------', request.data)
        print('------request.user-------', request.user)
        print('------request.user.id-------', request.user.id)
        print('------cookie_value-------', cookie_value)
        print('------user_ip-------', user_ip)
        print('------file_path-------', file_path)
        print('------video_id---request.data.get(videoId)----', request.data.get('videoId'))

        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        x, y, timestamp, video_id = data.get('x'), data.get('y'), data.get('timestamp'), data.get('videoId')

        click_data = {
            "coordinates": [x, y, x + 1, y + 1],
            "confidence": 1.0,
            "timestamp": timestamp,
            "videoId": video_id
        }
        print('------click_data-------', click_data)

        # # Сохраняем json-файл (словарь, не список!) в корне проекта, этот блок потом следует удалить
        # with open(f"{video_id}.json", "w") as f:
        #     json.dump(click_data, f)
        #     print('------type(f)-------', type(f))

        # # Сохраняем json-файл (словарь, не список!) в папку media
        # with open(file_path, 'w') as file:
        #     json.dump(data, file)
        # file_data = {'user_id': user_id, 'user_ip': user_ip, 'video_id': video_id, 'file_path': file_path}
        # print('------file_data----user_id-------', user_id, type(user_id))
        # print('------file_data----user_ip-------', user_ip, type(user_ip))
        # print('------file_data----video_id-------', video_id, type(video_id))
        # print('------file_data----file_path-------', file_path, type(file_path))
        # serializer = UserFilesSerializer(data=file_data)

        # Если файл уже существует, читаем его содержимое
        if os.path.exists(file_path):
            print('------if os.path.exists(file_path)-----*****--')
            with open(file_path, 'r') as file:
                current_data = json.load(file)
                print('------if os.path.exists(file_path)---current_data-------', current_data, type(current_data))
        else:
            print('------else-----*****--')
            current_data = []  # Или создаем новый список
            print('------else---current_data-------', current_data, type(current_data))

        current_data.append(data)  # Добавляем новые данные в список
        print('------3---current_data-------', current_data, type(current_data))

        # Записываем список с данными в файл
        with open(file_path, 'w') as file:
            json.dump(current_data, file)

        # Проверяем наличие записи с такими же данными в базе
        if not UserFiles.objects.filter(user_id=user_id, user_ip=user_ip, video_id=video_id,
                                        file_path=file_path).exists():
            file_data = {'user_id': user_id, 'user_ip': user_ip, 'video_id': video_id, 'file_path': file_path}
            serializer = UserFilesSerializer(data=file_data)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Запланировать очистку через 24 часа - но сначала разобраться с Redis !!!
        # clean_up_files.apply_async(countdown=86400)  # 24 часа = 86400 секунд
        # clean_up_files.apply_async(args=[user_id], countdown=86400)  # 24 часа = 86400 секунд
        # clean_up_files.apply_async((user_id,), countdown=86400)  # 24 часа = 86400 секунд

        return Response({'status': 'success', 'message': 'File saved successfully'}, status=status.HTTP_200_OK)
