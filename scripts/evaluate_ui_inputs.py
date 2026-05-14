import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.crop_service import CropPredictionService
from app.schemas.prediction_schema import PredictionInputSchema

payload = {
    'nitrogen': 100.0,
    'phosphorus': 35.0,
    'potassium': 60.0,
    'ph': 6.0,
    'temperature': 28.0,
    'rainfall': 1800.0,
    'region': 'Southsouth',  # Changed to Southsouth as suggested by the bot previously
    'state': 'Cross River',
    'agro_zone': 'Humid Forest',
    'soil_type': 'Clayey',
    'farm_size_ha': 1.0,
    'pest_type': 'None',
    'pest_severity': 'Low',
    'rainfall_variability': 'Normal',
    'labor_input': 'Medium'
}

try:
    schema = PredictionInputSchema()
    validated_data = schema.load(payload)
    print("Validated Data:", validated_data)

    service = CropPredictionService()
    
    print("\n--- CROP PREDICTION ---")
    prediction = service.predict(validated_data)
    print(f"Primary Recommendation: {prediction['recommended_crop']} (Probability: {prediction['probability']:.2%})")
    for rec in prediction['top_recommendations']:
        print(f"  - {rec['crop']}: {rec['probability']:.2%}")

except Exception as e:
    print(f"Error: {e}")
