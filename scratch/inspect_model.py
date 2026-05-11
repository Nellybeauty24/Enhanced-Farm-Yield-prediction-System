from catboost import CatBoostClassifier
import pandas as pd
import numpy as np
import os

model_path = os.path.join("models", "crop_model.cbm")
model = CatBoostClassifier()
model.load_model(model_path)

print("Classes length:", len(model.classes_))
print("Classes:", model.classes_)

# Create dummy input
df_input = pd.DataFrame([{
    'region': 'Unknown',
    'state': 'Unknown',
    'agro_zone': 'Unknown',
    'soil_type': 'Unknown',
    'pest_type': 'None',
    'pest_severity': 'Low',
    'rainfall_variability': 'Medium',
    'labor_input': 'Medium',
    'soil_nitrogen': 10,
    'soil_phosphorus': 10,
    'soil_potassium': 10,
    'soil_pH': 7,
    'temperature_C': 25,
    'rainfall_mm': 100,
    'farm_size_ha': 1.0,
    'soil_fertility_index': 30,
    'np_ratio': 1,
    'climate_index': 2500,
    'ph_stress': 0,
    'n_ph_inter': 70,
    'p_ph_inter': 70,
    'rain_temp_ratio': 4
}])

probs = model.predict_proba(df_input)[0]
print("Probs shape:", probs.shape)
print("Probs:", probs)

top_indices = np.argsort(probs)[::-1][:3]
top_crops = [
    {
        "crop": str(model.classes_[i]),
        "probability": float(probs[i])
    } 
    for i in top_indices
]
print("Top crops:", top_crops)
