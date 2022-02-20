from abc import ABC, abstractmethod
import numpy as np


class MobileFaceNet(ABC):

    @abstractmethod
    def load_model(self, model_path):
        pass

    @staticmethod
    def preprocess_image(img):
        img = img - 127.5
        img = img * 0.0078125

        return np.expand_dims(img, axis=0)

    @abstractmethod
    def calculate_embedding(self, face_image):
        pass
