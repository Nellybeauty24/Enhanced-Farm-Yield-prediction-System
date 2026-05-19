from app.services.crop_service import CropPredictionService

service = CropPredictionService()

# UI parameters from user's screen
payload = {
    'nitrogen': 85,
    'phosphorus': 40,
    'potassium': 60,
    'ph': 6.5,
    'temperature': 32.5,
    'rainfall': 650,
    'humidity': 44.9,
    'agro_zone': 'Sudan Savanna',
    'soil_type': 'Loamy'
}

print("Running prediction for UI parameters on the newly loaded crop model...")
res = service.predict(payload)
print(f"Prediction Result: {res}")
