from abc import ABC, abstractmethod
import numpy as np

def import_tensorflow():
    import os
    # https://stackoverflow.com/questions/40426502/is-there-a-way-to-suppress-the-messages-tensorflow-prints/40426709
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
    import warnings
    # https://stackoverflow.com/questions/15777951/how-to-suppress-pandas-future-warning
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=Warning)
    import tensorflow as tf
    tf.get_logger().setLevel('INFO')
    tf.autograph.set_verbosity(0)
    import logging
    tf.get_logger().setLevel(logging.ERROR)
    return tf

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
