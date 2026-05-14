"""
Quick smoke test for both models against known crop profiles.
"""
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
from catboost import CatBoostClassifier, CatBoostRegressor
print("=" * 70)
print("  ENHANCED FARM YIELD PREDICTION - MODEL SMOKE TEST")
print("=" * 70)

# ─── Load Models ──────────────────────────────────────────────────────────────
crop_model = CatBoostClassifier()
crop_model.load_model('models/crop_model.cbm')
print("\n✓ Crop classification model loaded")

yield_model = CatBoostRegressor()
yield_model.load_model('models/catboost_model.cbm')
print("✓ Yield prediction model loaded")

# ─── Test Scenarios ───────────────────────────────────────────────────────────
# Each scenario has parameters tuned to a specific crop's ideal range
scenarios = [
    {
        "name": "Rice farmer in Rivers (Humid Forest)",
        "expected": "Rice",
        "params": {
            'region': 'Southsouth', 'state': 'Rivers', 'agro_zone': 'Humid Forest',
            'soil_type': 'Clay', 'pest_type': 'None', 'pest_severity': 'None',
            'rainfall_variability': 'Normal', 'labor_input': 'Medium',
            'soil_nitrogen': 90, 'soil_phosphorus': 30, 'soil_potassium': 50,
            'soil_pH': 5.5, 'temperature_C': 28, 'rainfall_mm': 1800,
            'humidity': 85, 'farm_size_ha': 2.0,
        }
    },
    {
        "name": "Sorghum farmer in Kano (Sudan Savanna)",
        "expected": "Sorghum",
        "params": {
            'region': 'Northwest', 'state': 'Kano', 'agro_zone': 'Sudan Savanna',
            'soil_type': 'Sandy', 'pest_type': 'None', 'pest_severity': 'None',
            'rainfall_variability': 'Low', 'labor_input': 'Low',
            'soil_nitrogen': 40, 'soil_phosphorus': 30, 'soil_potassium': 50,
            'soil_pH': 6.8, 'temperature_C': 36, 'rainfall_mm': 600,
            'humidity': 40, 'farm_size_ha': 3.0,
        }
    },
    {
        "name": "Maize farmer in Kaduna (N. Guinea Savanna)",
        "expected": "Maize",
        "params": {
            'region': 'Northwest', 'state': 'Kaduna', 'agro_zone': 'Northern Guinea Savanna',
            'soil_type': 'Loamy', 'pest_type': 'None', 'pest_severity': 'None',
            'rainfall_variability': 'Normal', 'labor_input': 'High',
            'soil_nitrogen': 110, 'soil_phosphorus': 55, 'soil_potassium': 70,
            'soil_pH': 6.5, 'temperature_C': 26, 'rainfall_mm': 900,
            'humidity': 60, 'farm_size_ha': 4.0,
        }
    },
    {
        "name": "Cassava farmer in Edo (Humid Forest)",
        "expected": "Cassava",
        "params": {
            'region': 'Southsouth', 'state': 'Edo', 'agro_zone': 'Humid Forest',
            'soil_type': 'Sandy Loam', 'pest_type': 'None', 'pest_severity': 'None',
            'rainfall_variability': 'Normal', 'labor_input': 'Medium',
            'soil_nitrogen': 20, 'soil_phosphorus': 15, 'soil_potassium': 140,
            'soil_pH': 5.2, 'temperature_C': 29, 'rainfall_mm': 1500,
            'humidity': 75, 'farm_size_ha': 1.5,
        }
    },
    {
        "name": "Onions farmer in Sokoto (Sahel Savanna)",
        "expected": "Onions",
        "params": {
            'region': 'Northwest', 'state': 'Sokoto', 'agro_zone': 'Sahel Savanna',
            'soil_type': 'Sandy Loam', 'pest_type': 'None', 'pest_severity': 'None',
            'rainfall_variability': 'Low', 'labor_input': 'Medium',
            'soil_nitrogen': 60, 'soil_phosphorus': 50, 'soil_potassium': 90,
            'soil_pH': 7.0, 'temperature_C': 22, 'rainfall_mm': 450,
            'humidity': 35, 'farm_size_ha': 1.0,
        }
    },
]

# ─── Feature Engineering (must match training) ───────────────────────────────
def prepare_input(params):
    """Build DataFrame with engineered features matching training pipeline."""
    row = dict(params)
    row['soil_fertility_index'] = row['soil_nitrogen'] + row['soil_phosphorus'] + row['soil_potassium']
    row['np_ratio'] = row['soil_nitrogen'] / (row['soil_phosphorus'] + 1e-6)
    row['climate_index'] = row['rainfall_mm'] * row['temperature_C']
    row['ph_stress'] = abs(row['soil_pH'] - 7.0)
    row['n_ph_inter'] = row['soil_nitrogen'] * row['soil_pH']
    row['p_ph_inter'] = row['soil_phosphorus'] * row['soil_pH']
    row['rain_temp_ratio'] = row['rainfall_mm'] / (row['temperature_C'] + 1e-6)
    return pd.DataFrame([row])


# ─── Run Tests ────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print(f"  {'Scenario':<45} {'Expected':<10} {'Got':<10} {'Conf':>6} {'Yield':>10}")
print("─" * 70)

passed = 0
for s in scenarios:
    df = prepare_input(s['params'])

    # Crop prediction
    crop_features = [
        'agro_zone', 'soil_type',
        'pest_type', 'pest_severity', 'rainfall_variability', 'labor_input',
        'soil_nitrogen', 'soil_phosphorus', 'soil_potassium',
        'soil_pH', 'temperature_C', 'rainfall_mm', 'humidity', 'farm_size_ha',
        'soil_fertility_index', 'np_ratio', 'climate_index', 'ph_stress',
        'n_ph_inter', 'p_ph_inter', 'rain_temp_ratio'
    ]
    crop_pred_raw = crop_model.predict(df[crop_features])
    # CatBoost can return nested arrays like [['Rice']] — flatten to string
    crop_pred = crop_pred_raw.flatten()[0]
    if not isinstance(crop_pred, str):
        crop_pred = str(crop_pred)
    crop_proba = crop_model.predict_proba(df[crop_features])[0]
    confidence = max(crop_proba)

    # Yield prediction — must provide ALL 27 features the model expects
    yield_row = dict(s['params'])
    yield_row['crop_type'] = crop_pred
    yield_row['crop_variety'] = 'Unknown'
    yield_row['fertilizer_type'] = 'NPK'
    yield_row['fertilizer_amount_kg_ha'] = 100.0
    yield_row['irrigation_type'] = 'Rainfed'
    yield_row['temperature_stress'] = 'None'
    yield_row['extreme_weather'] = 'None'
    yield_row['soil_degradation'] = 'None'
    yield_row['soil_fertility_index'] = yield_row['soil_nitrogen'] + yield_row['soil_phosphorus'] + yield_row['soil_potassium']
    yield_row['np_ratio'] = yield_row['soil_nitrogen'] / (yield_row['soil_phosphorus'] + 1e-6)
    yield_row['climate_index'] = yield_row['rainfall_mm'] * yield_row['temperature_C']
    yield_df = pd.DataFrame([yield_row])
    yield_pred = yield_model.predict(yield_df[yield_model.feature_names_])[0]

    match = "✓" if crop_pred == s['expected'] else "✗"
    status = crop_pred == s['expected']
    passed += status

    print(f"  {match} {s['name']:<43} {s['expected']:<10} {crop_pred:<10} {confidence:>5.1%} {yield_pred:>8.0f} kg/ha")

print("─" * 70)
print(f"\n  Results: {passed}/{len(scenarios)} scenarios passed")
print("=" * 70)
