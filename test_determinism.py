from app.services.crop_service import CropPredictionService
service = CropPredictionService()
payload = {
    'nitrogen': 50, 'phosphorus': 30, 'potassium': 40,
    'ph': 6.5, 'temperature': 25, 'rainfall': 1000,
    'humidity': 60, 'agro_zone': 'Derived Savanna', 'soil_type': 'Loamy'
}
res1 = service.predict(payload)
print(f"Crop Prediction: {res1}")

# Test Yield Prediction
yield_payload = {**payload, 'crop_type': res1['recommended_crop']}
yield_res = service.predict_yield(yield_payload)
print(f"Yield Prediction: {yield_res} kg/ha")

