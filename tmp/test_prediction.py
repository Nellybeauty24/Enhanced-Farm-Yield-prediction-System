from app.services.crop_service import CropPredictionService
from app.services.recommendation_service import RecommendationService
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)

crop_service = CropPredictionService()
recommendation_service = RecommendationService()

data = {
    "nitrogen": 30,
    "phosphorus": 30,
    "potassium": 49,
    "ph": 4.7,
    "temperature": 44.6,
    "rainfall": 499.7
}

try:
    print("Testing crop_service.predict...")
    predicted_crop, confidence = crop_service.predict(data)
    print(f"Predicted: {predicted_crop}, Confidence: {confidence}")
    
    print("Testing recommendation_service.generate_recommendations...")
    recs = recommendation_service.generate_recommendations(predicted_crop, data, confidence)
    print(f"Recommendations count: {len(recs)}")
    for r in recs:
        print(f"- {r}")
except Exception as e:
    import traceback
    traceback.print_exc()
