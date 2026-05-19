from app.services.crop_service import CropPredictionService

service = CropPredictionService()

# Starvation matrix payload
payload = {
    'nitrogen': 24, 
    'phosphorus': 20, 
    'potassium': 118,
    'ph': 6.5, 
    'temperature': 28, 
    'rainfall': 950,
    'humidity': 65, 
    'agro_zone': 'Northern Guinea Savanna', 
    'soil_type': 'Sandy'
}

print("Running prediction for starvation matrix (Low N/P, Potassium Sink, Sandy Soil, Northern Guinea Savanna)...")
res = service.predict(payload)
print(f"Crop Prediction: {res}")

yield_payload = {**payload, 'crop_type': res['recommended_crop']}
yield_res = service.predict_yield(yield_payload)
print(f"Yield Prediction: {yield_res:.2f} kg/ha")
