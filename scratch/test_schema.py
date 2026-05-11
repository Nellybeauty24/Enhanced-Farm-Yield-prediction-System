import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas.prediction_schema import PredictionOutputSchema

schema = PredictionOutputSchema()
response_data = {
    "recommended_crop": "Maize",
    "probability": 0.17,
    "top_recommendations": [{"crop": "Maize", "probability": 0.17}, {"crop": "Rice", "probability": 0.10}],
    "recommendations": ["Do this", "Do that"],
    "input_summary": {"nitrogen": 10}
}
print(schema.dump(response_data))
