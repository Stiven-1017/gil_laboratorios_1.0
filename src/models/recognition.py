import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
from tensorflow.keras.models import load_model # type: ignore

import os
model_path = os.path.join(os.path.dirname(__file__), 'microscopio_model.h5')
model = load_model(model_path)
def detectar_equipo(frame):
    imagen = cv2.resize(frame, (224, 224))
    imagen = img_to_array(imagen)
    imagen = np.expand_dims(imagen, axis=0)
    imagen = imagen / 255.0  # Normalizar
    pred = model.predict(imagen)[0][0]
    if pred > 0.3:
        return "microscopio", pred
    else:
        return None, None