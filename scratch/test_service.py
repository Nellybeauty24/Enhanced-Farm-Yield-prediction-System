import sys
import os

sys.path.append('/app')
from app.services.crop_service import CropPredictionService

service = CropPredictionService()
input_data = {
    'nitrogen': 10,
    'phosphorus': 10,
    'potassium': 10,
    'ph': 7,
    'temperature': 25,
    'rainfall': 100
}

try:
    result = service.predict(input_data)
    print("PREDICTION_RESULT:")
    print(result)
except Exception as e:
    print("ERROR:", e)
