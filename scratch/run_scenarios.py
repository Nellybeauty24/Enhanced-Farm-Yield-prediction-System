import pandas as pd
from app.services.crop_service import CropPredictionService

service = CropPredictionService()

scenarios = [
    {
        "name": "Scenario 1: High-Input Cereal/Tuber Belt",
        "payload": {
            'nitrogen': 120, 'phosphorus': 90, 'potassium': 100,
            'ph': 6.2, 'temperature': 27, 'rainfall': 1200,
            'humidity': 70, 'agro_zone': 'Derived Savanna', 'soil_type': 'Loamy'
        }
    },
    {
        "name": "Scenario 2: Acidic High-Rainfall Belt",
        "payload": {
            'nitrogen': 60, 'phosphorus': 40, 'potassium': 50,
            'ph': 4.8, 'temperature': 26, 'rainfall': 2100,
            'humidity': 85, 'agro_zone': 'Humid Forest', 'soil_type': 'Clayey'
        }
    },
    {
        "name": "Scenario 3: Semi-Arid Grain/Onion Belt",
        "payload": {
            'nitrogen': 45, 'phosphorus': 30, 'potassium': 85,
            'ph': 7.2, 'temperature': 32, 'rainfall': 450,
            'humidity': 35, 'agro_zone': 'Sahel Savanna', 'soil_type': 'Sandy'
        }
    },
    {
        "name": "Scenario 4: Starvation Matrix (High Potassium Sink)",
        "payload": {
            'nitrogen': 24, 'phosphorus': 20, 'potassium': 118,
            'ph': 6.5, 'temperature': 28, 'rainfall': 950,
            'humidity': 65, 'agro_zone': 'Northern Guinea Savanna', 'soil_type': 'Sandy'
        }
    }
]

for sc in scenarios:
    print(f"\n=== {sc['name']} ===")
    res = service.predict(sc['payload'])
    print(f"Top 3 Crops & Confidences:")
    for rank, item in enumerate(res['top_recommendations'], 1):
        print(f"  {rank}. {item['crop']}: {item['probability']:.4f}")
    
    # Predict yield for the top crop
    yield_payload = {**sc['payload'], 'crop_type': res['recommended_crop']}
    yield_val = service.predict_yield(yield_payload)
    print(f"Predicted Yield for {res['recommended_crop']}: {yield_val:.2f} kg/ha")
