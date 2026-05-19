from app.services.crop_service import CropPredictionService
import json
from scripts.generate_dataset import calculate_suitability

with open('data/crop_requirements.json', 'r') as f:
    crop_reqs = json.load(f)

# Payload parameters
nitrogen = 130
phosphorus = 85
potassium = 150
ph = 6.3
temperature = 27.5
rainfall = 1800
humidity = 75
agro_zone = 'Humid Forest'
soil_type = 'Loamy'

print("Calculating compatibility for each crop under high-nutrient Humid Forest conditions:")
for crop_name, crop_req in crop_reqs.items():
    compat = calculate_suitability(
        crop_name, crop_req, nitrogen, phosphorus, potassium, ph,
        rainfall, temperature, humidity, soil_type, agro_zone
    )
    print(f"  {crop_name.capitalize()}: {compat:.4f}")

# Running actual model prediction
service = CropPredictionService()
res = service.predict({
    'nitrogen': nitrogen,
    'phosphorus': phosphorus,
    'potassium': potassium,
    'ph': ph,
    'temperature': temperature,
    'rainfall': rainfall,
    'humidity': humidity,
    'agro_zone': agro_zone,
    'soil_type': soil_type
})
print(f"Model Prediction: {res}")
