import os

from django.shortcuts import render
import cv2
import numpy as np
import tensorflow as tf
import json

class ObjectDetector:
    @staticmethod
    def detect_objects(frame):
        model = tf.saved_model.load(
            '../ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Предварительно обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели

        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)  # Преобразование кадра в тензор
        detections = infer(input_tensor)  # Применение модели к тензору для обнаружения объектов

        boxes = detections['detection_boxes'][
            0].numpy()  # Извлечение границ обнаруженных объектов из результатов модели
        classes = detections['detection_classes'][0].numpy().astype(np.int32)  # Извлечение классов ...
        scores = detections['detection_scores'][0].numpy()  # Извлечение оценок ...

        return boxes, classes, scores

    def process_video(self, video_path):

        model = tf.saved_model.load(
            '../ssd_mobilenet_v2_coco_2018_03_29/saved_model')  # Предварительно обученная модель
        infer = model.signatures["serving_default"]  # Получение подписи 'serving_default' из модели

        cap = cv2.VideoCapture(video_path)  # Инициализация объекта видеозахвата с помощью cv2.VideoCapture
        detections_data = []  # Инициализация пустого списка для обнаруженных объектов
        print('---1------detections_data-----', detections_data)
        print('---1------cap-----', cap)

        # # ОБРАБАТЫВАЕМ КАЖДЫЙ КАДР:
        #
        # while cap.isOpened():
        #     print('---1------while cap.isOpened()----')
        #     ret, frame = cap.read()
        #     print('---1------ret-----', ret)
        #     if not ret:
        #         print('---1------if not ret-----')
        #         break
        #
        #     boxes, classes, scores = self.detect_objects(frame)
        #
        #     confidence_threshold = 0.5
        #
        #     for box, score, cls in zip(boxes, scores, classes):
        #         print('---1------box-----', box)
        #         print('---1------score-----', score)
        #         print('---1------cls-----', cls)
        #         if cls == 1 and score >= confidence_threshold:
        #             height, width, _ = frame.shape
        #             ymin, xmin, ymax, xmax = box
        #             ymin = int(ymin * height)
        #             xmin = int(xmin * width)
        #             ymax = int(ymax * height)
        #             xmax = int(xmax * width)
        #             print('---1------ymin, xmin, ymax, xmax-----', ymin, xmin, ymax, xmax)
        #
        #             timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # Получение времени в секундах
        #             print('---1------timestamp-----', timestamp)
        #
        #             cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        #             detections_data.append({
        #                 "coordinates": [xmin, ymin, xmax, ymax],
        #                 "confidence": float(score),  # Здесь произошли изменения
        #                 "timestamp": timestamp
        #             })
        #             print('---2------detections_data-----', detections_data)
        #
        #     cv2.imshow('Video', frame)
        #
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        #
        # cap.release()
        # cv2.destroyAllWindows()
        #
        # with open("778899.json", "w") as f:
        #     json.dump(detections_data, f)

        # ОБРАБАТЫВАЕМ КАЖДЫЙ 100-й КАДР:

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
                video_path = "../media/source_video_files/test.mp4"
                video_name = os.path.basename(video_path).split('.')[0]  # Извлечение имени файла без расширения
                # Изменение имени сохраняемого JSON-файла с использованием имени исходного видеофайла
                json_file_name = f"{video_name}_detections.json"
                with open(json_file_name, "w") as f:
                    json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON

                # with open("778899.json", "w") as f:
                #     json.dump(detections_data, f)  # Запись обнаруженных данных в формате JSON

            frame_count += 1  # Увеличение счетчика кадров

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Проверка, была ли нажата клавиша "q" для выхода
                break  # Прерывание цикла обработки кадров

        cap.release()  # Освобождение захваченного видеопотока после обработки видео
        cv2.destroyAllWindows()  # Закрытие всех окон, созданных OpenCV


# Запуск обработки видео с помощью экземпляра ObjectDetector
if __name__ == "__main__":  # Проверка, запущен ли скрипт напрямую, а не импортирован как модуль
    video_path = "../media/source_video_files/test.mp4"
    obj_detector = ObjectDetector()  # Создание экземпляра класса ObjectDetector для обработки видео
    obj_detector.process_video(video_path)
