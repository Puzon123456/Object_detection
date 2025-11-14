import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2
import matplotlib.pyplot as plt
import warnings
import os
from PIL import Image
from django.conf import settings

warnings.filterwarnings('ignore')

class ObjectDetector:
    def __init__(self, model_url):
        """
        Inicjalizacja detektora obiektów
        """
        print("Ładowanie modelu z TensorFlow Hub...")
        self.detector = hub.load(model_url)
        print("Model załadowany pomyślnie!")
        
    def load_and_preprocess_image(self, image_path):
        """
        Wczytanie oraz konwersja obrazu z ścieżki pliku
        """
        image_np = np.asarray(np.array(Image.open(image_path)))
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]
        input_tensor = input_tensor[:, :, :, :3]
        
        return image_np, input_tensor
    
    def load_and_preprocess_from_file(self, image_file):
        """
        Wczytanie oraz konwersja obrazu z pliku Django
        """
        # Odczytaj dane obrazu
        image_data = image_file.read()
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Konwersja do tensoru
        image_tensor = tf.convert_to_tensor(image)
        image_tensor = image_tensor[tf.newaxis, ...]
        image_tensor = image_tensor[:, :, :, :3]
        
        return image, image_tensor
    
    def detect_objects(self, image_tensor):
        """
        Wykonanie detekcji obiektów na obrazie
        """
        results = self.detector(image_tensor)
        return results
    
    def process_detections(self, results, confidence_threshold=0.24):
        """
        Przetworzenie wyników detekcji
        """
        # Pobranie wyników
        boxes = results['detection_boxes'][0].numpy()
        scores = results['detection_scores'][0].numpy()
        classes = results['detection_classes'][0].numpy().astype(int)
        
        # Filtrowanie detekcji na podstawie progu pewności
        valid_detections = scores > confidence_threshold
        filtered_boxes = boxes[valid_detections]
        filtered_scores = scores[valid_detections]
        filtered_classes = classes[valid_detections]
        
        return filtered_boxes, filtered_scores, filtered_classes
    
    def draw_detections(self, image, boxes, scores, classes, class_names):
        """
        Rysowanie detection boxes i etykiet na obrazie
        """
        image_with_detections = image.copy()
        height, width = image.shape[:2]
        
        for i, (box, score, class_id) in enumerate(zip(boxes, scores, classes)):
            # Konwersja współrzędnych
            ymin, xmin, ymax, xmax = box
            xmin = int(xmin * width)
            xmax = int(xmax * width)
            ymin = int(ymin * height)
            ymax = int(ymax * height)
            
            # Rysowanie bounding box
            cv2.rectangle(image_with_detections, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            
            # Przygotowanie etykiety
            label = f"{class_names[class_id]}: {score:.2f}"
            
            # Rysowanie etykiety
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(image_with_detections, 
                         (xmin, ymin - label_size[1] - 10),
                         (xmin + label_size[0], ymin),
                         (0, 255, 0), -1)
            cv2.putText(image_with_detections, label, 
                       (xmin, ymin - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return image_with_detections
    
    def save_processed_image(self, image, filename):
        """
        Zapis przetworzonego obrazu
        """
        # Konwersja RGB to BGR dla OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Ścieżka do zapisu
        filepath = os.path.join(settings.MEDIA_ROOT, 'detection_images/processed/', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Zapis obrazu
        cv2.imwrite(filepath, image_bgr)
        
        return f'detection_images/processed/{filename}'

# Słownik klas COCO
COCO_CLASSES = {
    1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane',
    6: 'bus', 7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light',
    11: 'fire hydrant', 13: 'stop sign', 14: 'parking meter', 15: 'bench',
    16: 'bird', 17: 'cat', 18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow',
    22: 'elephant', 23: 'bear', 24: 'zebra', 25: 'giraffe', 27: 'backpack',
    28: 'umbrella', 31: 'handbag', 32: 'tie', 33: 'suitcase', 34: 'frisbee',
    35: 'skis', 36: 'snowboard', 37: 'sports ball', 38: 'kite', 39: 'baseball bat',
    40: 'baseball glove', 41: 'skateboard', 42: 'surfboard', 43: 'tennis racket',
    44: 'bottle', 46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
    51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
    56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
    61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
    67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
    75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
    80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
    86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'
}