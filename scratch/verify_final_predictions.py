from app.services.crop_service import CropPredictionService

service = CropPredictionService()

# 1. Paradox of Perfection (High Nutrient, Yam expected)
pop_payload = {
    'nitrogen': 130,
    'phosphorus': 85,
    'potassium': 150,
    'ph': 6.3,
    'temperature': 27.5,
    'rainfall': 1800,
    'humidity': 75,
    'agro_zone': 'Humid Forest',
    'soil_type': 'Loamy'
}

print("--- Testing Paradox of Perfection Matrix ---")
pop_res = service.predict(pop_payload)
print(f"Crop Prediction: {pop_res}")

yield_payload = {**pop_payload, 'crop_type': pop_res['recommended_crop'], 'crop_variety': 'TDr 179'}
pop_yield = service.predict_yield(yield_payload)
print(f"Predicted Yield: {pop_yield:.2f} kg/ha\n")


# 2. Cement Matrix (Clay, 1300mm rain, Maize expected)
cement_payload = {
    'nitrogen': 60,
    'phosphorus': 40,
    'potassium': 50,
    'ph': 6.0,
    'temperature': 26.0,
    'rainfall': 1300,
    'humidity': 70,
    'agro_zone': 'Derived Savanna',
    'soil_type': 'Clayey'
}

print("--- Testing Cement Matrix ---")
cement_res = service.predict(cement_payload)
print(f"Crop Prediction: {cement_res}")

cement_yield_payload = {**cement_payload, 'crop_type': cement_res['recommended_crop'], 'crop_variety': 'Oba Super II'}
cement_yield = service.predict_yield(cement_yield_payload)
print(f"Predicted Yield: {cement_yield:.2f} kg/ha")
