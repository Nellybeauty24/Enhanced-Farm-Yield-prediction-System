from app.services.crop_service import CropPredictionService

service = CropPredictionService()

payload = {
    'nitrogen': 50,
    'phosphorus': 45,
    'potassium': 30,
    'ph': 4.5,
    'temperature': 26.5,
    'rainfall': 2800,
    'humidity': 88,
    'agro_zone': 'Humid Forest',
    'soil_type': 'Clayey'
}

print("Running prediction for Humid Forest / Clayey / pH 4.5 / 2800mm scenario:")
res = service.predict(payload)
print(f"Prediction Result: {res}")
