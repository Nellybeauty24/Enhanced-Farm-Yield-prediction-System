from app.services.crop_service import CropPredictionService
service = CropPredictionService()
payload = {
    'nitrogen': 50, 'phosphorus': 30, 'potassium': 40,
    'ph': 6.5, 'temperature': 25, 'rainfall': 1000,
    'humidity': 60, 'agro_zone': 'Derived Savanna', 'soil_type': 'Loamy'
}
res1 = service.predict(payload)
res2 = service.predict(payload)
print(f"Res 1: {res1}")
print(f"Res 2: {res2}")
print(f"Deterministic? {res1 == res2}")
