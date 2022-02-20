import os
import platform

import numpy as np

from MobileFaceNet import MobileFaceNet, import_tensorflow

if platform.machine() == "armv7l":
    from tflite_runtime.interpreter import Interpreter
else:
    Interpreter = import_tensorflow().lite.Interpreter


class MobileFaceNetLite(MobileFaceNet):

    def __init__(self):
        self.interpreter = None
        self.input_details = None
        self.output_details = None

    def load_model(self, model_path):
        model_exp = os.path.expanduser(model_path)
        if os.path.isfile(model_exp):
            # Load the TFLite model and allocate tensors.
            self.interpreter = Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()

            # Get input and output tensors.
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            print("Loaded MobileFaceNet model")
        else:
            print('Found no model.')

    def calculate_embedding(self, face_image):
        face_image = face_image.astype(np.float32)
        face_image = self.preprocess_image(face_image)

        self.interpreter.invoke()

        self.interpreter.set_tensor(self.input_details[0]['index'], face_image)
        return self.interpreter.get_tensor(self.output_details[0]['index'])
