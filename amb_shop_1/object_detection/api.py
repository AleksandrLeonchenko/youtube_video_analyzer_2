import cv2
import numpy as np
import tensorflow as tf
import json


class ObjectDetector:
    @staticmethod
    def detect_objects(frame):
        model = tf.saved_model.load('../ssd_mobilenet_v2_coco_2018_03_29/saved_model')
        infer = model.signatures["serving_default"]

        input_tensor = tf.convert_to_tensor([frame], dtype=tf.uint8)
        detections = infer(input_tensor)

        boxes = detections['detection_boxes'][0].numpy()
        classes = detections['detection_classes'][0].numpy().astype(np.int32)
        scores = detections['detection_scores'][0].numpy()

        return boxes, classes, scores

    def process_video(self, video_path):

        model = tf.saved_model.load('../ssd_mobilenet_v2_coco_2018_03_29/saved_model')
        infer = model.signatures["serving_default"]

        cap = cv2.VideoCapture(video_path)
        # cap = cv2.VideoCapture("test.mp4")
        detections_data = []
        print('---1------detections_data-----', detections_data)
        print('---1------cap-----', cap)


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


        frame_count = 0  # Счетчик кадров

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % 200 == 0:  # Проверка для каждого 200-го кадра
                boxes, classes, scores = self.detect_objects(frame)

                confidence_threshold = 0.5

                for box, score, cls in zip(boxes, scores, classes):
                    print('---1------box-----', box)
                    print('---1------score-----', score)
                    print('---1------cls-----', cls)
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

                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        detections_data.append({
                            "coordinates": [xmin, ymin, xmax, ymax],
                            "confidence": float(score),  # Здесь произошли изменения
                            "timestamp": timestamp
                        })
                        print('---2------detections_data-----', detections_data)

                with open("778899.json", "w") as f:
                    json.dump(detections_data, f)

            frame_count += 1  # Увеличение счетчика кадров

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()



        # with open("778899.json", "w") as f:
        #     json.dump(detections_data, f)


if __name__ == "__main__":
    obj_detector = ObjectDetector()
    obj_detector.process_video("../media/source_video_files/test.mp4")
