"""
Dataset Generator for Enhanced Farm Yield Prediction System.
Generates a scientifically differentiated synthetic dataset with realistic
crop-environment correlations based on Nigerian agricultural zones.

Usage:
    python scripts/generate_dataset.py
"""

import csv
import json
import random
import os
import math

# ─── Configuration ────────────────────────────────────────────────────────────
OUTPUT_PATH = 'data/nigeria_agri_yield_enhanced.csv'
REQUIREMENTS_PATH = 'data/crop_requirements.json'
NUM_RECORDS = 20000
RANDOM_SEED = 42

# ─── Nigerian Geographic Data ─────────────────────────────────────────────────
AGRO_ZONE_CONFIG = {
    'Humid Forest': {
        'regions': ['Southwest', 'Southsouth', 'Southeast'],
        'states': {
            'Southwest': ['Lagos', 'Ogun', 'Ondo', 'Ekiti', 'Osun', 'Oyo'],
            'Southsouth': ['Rivers', 'Bayelsa', 'Delta', 'Edo', 'Cross River', 'Akwa Ibom'],
            'Southeast': ['Abia', 'Anambra', 'Enugu', 'Imo', 'Ebonyi'],
        },
        'base_temp': (26, 32),
        'base_rainfall': (1500, 2500),
        'base_humidity': (70, 95),
    },
    'Derived Savanna': {
        'regions': ['Southwest', 'Southsouth', 'Northcentral'],
        'states': {
            'Southwest': ['Oyo', 'Osun', 'Kwara'],
            'Southsouth': ['Edo', 'Delta'],
            'Northcentral': ['Kwara', 'Kogi', 'Benue', 'Niger', 'Nasarawa'],
        },
        'base_temp': (25, 33),
        'base_rainfall': (1000, 1600),
        'base_humidity': (55, 80),
    },
    'Northern Guinea Savanna': {
        'regions': ['Northcentral', 'Northwest', 'Northeast'],
        'states': {
            'Northcentral': ['Plateau', 'Nasarawa', 'Niger'],
            'Northwest': ['Kaduna', 'Katsina'],
            'Northeast': ['Taraba', 'Adamawa', 'Bauchi'],
        },
        'base_temp': (22, 34),
        'base_rainfall': (800, 1200),
        'base_humidity': (40, 70),
    },
    'Sudan Savanna': {
        'regions': ['Northwest', 'Northeast'],
        'states': {
            'Northwest': ['Kano', 'Katsina', 'Zamfara', 'Sokoto', 'Kebbi'],
            'Northeast': ['Gombe', 'Bauchi', 'Yobe'],
        },
        'base_temp': (28, 38),
        'base_rainfall': (500, 900),
        'base_humidity': (30, 55),
    },
    'Sahel Savanna': {
        'regions': ['Northeast', 'Northwest'],
        'states': {
            'Northeast': ['Borno', 'Yobe'],
            'Northwest': ['Sokoto', 'Kebbi', 'Zamfara'],
        },
        'base_temp': (30, 42),
        'base_rainfall': (250, 600),
        'base_humidity': (20, 45),
    },
}

CROP_VARIETIES = {
    'Rice': ['FARO 44', 'FARO 52', 'NERICA-1', 'NERICA-4', 'Ofada'],
    'Cassava': ['TMS 30572', 'TME 419', 'TMS 98/0505', 'NR 8082', 'Oko-Iyawo'],
    'Yam': ['White Yam', 'Water Yam', 'Yellow Yam', 'Aerial Yam', 'Pona'],
    'Maize': ['SAMMAZ 14', 'SAMMAZ 15', 'Oba Super-1', 'DTMA', 'DMR-LSR-Y'],
    'Sorghum': ['SAMSORG 14', 'SAMSORG 17', 'SK 5912', 'CSR-01', 'ICSV 400'],
    'Beans': ['IT89KD-288', 'IT97K-499-35', 'IT90K-277-2', 'Sampea-7', 'Sampea-14'],
    'Onions': ['Red Creole', 'Bombay Red', 'Ex-Gidan', 'Dan Zaria', 'Dan Wuri'],
    'Tomato': ['UC82B', 'Roma VF', 'Tropimech', 'Dan Eka', 'Dan Mazari'],
    'Pepper': ['Nsukka Yellow', 'Tatase', 'Shombo', 'Atarugu', 'Bawa'],
}

SOIL_TYPES = ['Sandy', 'Sandy Loam', 'Loamy', 'Clay Loam', 'Clay', 'Lateritic', 'Alluvial']
PEST_SEVERITY = ['Low', 'Moderate', 'High', 'None']
RAINFALL_VARIABILITY = ['Low', 'Normal', 'Erratic', 'High']
LABOR_INPUT = ['Low', 'Medium', 'High']
PEST_TYPES_BY_CROP = {
    'Rice': ['Stem Borers', 'Rice Blast', 'Leaf Miners', 'None'],
    'Cassava': ['Cassava Mealybug', 'Green Spider Mite', 'Whiteflies', 'None'],
    'Yam': ['Yam Beetle', 'Nematodes', 'Scale Insects', 'None'],
    'Maize': ['Stem Borers', 'Fall Armyworm', 'Weevils', 'None'],
    'Sorghum': ['Stem Borers', 'Head Bug', 'Grain Mold', 'None'],
    'Beans': ['Pod Borers', 'Aphids', 'Bruchids', 'None'],
    'Onions': ['Thrips', 'Purple Blotch', 'Onion Maggot', 'None'],
    'Tomato': ['Tuta Absoluta', 'Whiteflies', 'Fruit Worm', 'None'],
    'Pepper': ['Aphids', 'Whiteflies', 'Pepper Weevil', 'None'],
}
TEMPERATURE_STRESS = ['None', 'Low', 'Moderate', 'High']
EXTREME_WEATHER = ['None', 'Flood', 'Drought', 'Hailstorm']
FERTILIZER_TYPES = ['NPK', 'Urea', 'Organic', 'SSP', 'None']
IRRIGATION_TYPES = ['Rainfed', 'Surface', 'Drip', 'Sprinkler', 'None']
SOIL_DEGRADATION = ['None', 'Low', 'Moderate', 'Severe']


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def rand_in(lo, hi, noise=0.0):
    """Random value in range with optional Gaussian noise beyond bounds."""
    base = random.uniform(lo, hi)
    if noise > 0:
        base += random.gauss(0, noise)
    return base


def generate_yield(crop_req, nitrogen, phosphorus, potassium, ph, rainfall, temperature, humidity, pest_severity, farm_size):
    """Generate a realistic yield based on how well conditions match crop requirements."""
    base = crop_req['base_yield']
    variance = crop_req['yield_variance']

    # Score each factor (0 to 1) based on how centered the value is in the ideal range
    def factor_score(val, lo, hi):
        mid = (lo + hi) / 2.0
        span = (hi - lo) / 2.0
        if span == 0:
            return 1.0
        dist = abs(val - mid) / span
        return max(0, 1.0 - dist * 0.5)

    n_score = factor_score(nitrogen, *crop_req['nitrogen'])
    p_score = factor_score(phosphorus, *crop_req['phosphorus'])
    k_score = factor_score(potassium, *crop_req['potassium'])
    ph_score = factor_score(ph, *crop_req['ph'])
    rain_score = factor_score(rainfall, *crop_req['rainfall'])
    temp_score = factor_score(temperature, *crop_req['temperature'])
    humid_score = factor_score(humidity, *crop_req['humidity'])

    # Weighted composite
    composite = (
        n_score * 0.15 + p_score * 0.10 + k_score * 0.10 +
        ph_score * 0.15 + rain_score * 0.20 + temp_score * 0.15 +
        humid_score * 0.15
    )

    # Pest penalty
    pest_penalty = {'None': 1.0, 'Low': 0.92, 'Moderate': 0.78, 'High': 0.60}
    composite *= pest_penalty.get(pest_severity, 0.85)

    # Farm size slight bonus (larger farms = slightly more efficient)
    size_factor = 1.0 + math.log10(max(farm_size, 0.1)) * 0.05

    yield_val = base * composite * size_factor + random.gauss(0, variance * 0.3)
    return max(200, round(yield_val, 1))


def generate_record(crop_name, crop_req, record_id):
    """Generate a single data record for a crop."""
    # Pick an agro-zone compatible with this crop
    compatible_zones = crop_req.get('agro_zones', list(AGRO_ZONE_CONFIG.keys()))
    zone_name = random.choice(compatible_zones)
    zone = AGRO_ZONE_CONFIG[zone_name]

    # Geography
    region = random.choice(zone['regions'])
    states = zone['states'].get(region, ['Unknown'])
    state = random.choice(states)

    # Soil parameters - from the crop's ideal range with noise for realism
    ph_lo, ph_hi = crop_req['ph']
    n_lo, n_hi = crop_req['nitrogen']
    p_lo, p_hi = crop_req['phosphorus']
    k_lo, k_hi = crop_req['potassium']
    temp_lo, temp_hi = crop_req['temperature']
    rain_lo, rain_hi = crop_req['rainfall']
    humid_lo, humid_hi = crop_req['humidity']

    # 85% of data within ideal range, 15% slightly outside (real-world noise)
    if random.random() < 0.85:
        nitrogen = round(rand_in(n_lo, n_hi, noise=2), 1)
        phosphorus = round(rand_in(p_lo, p_hi, noise=2), 1)
        potassium = round(rand_in(k_lo, k_hi, noise=3), 1)
        ph = round(rand_in(ph_lo, ph_hi, noise=0.1), 1)
        temperature = round(rand_in(temp_lo, temp_hi, noise=1), 1)
        rainfall = round(rand_in(rain_lo, rain_hi, noise=30), 1)
        humidity = round(rand_in(humid_lo, humid_hi, noise=3), 1)
    else:
        # Out-of-range samples (farmer planted in suboptimal conditions)
        spread = 0.3
        nitrogen = round(rand_in(n_lo - (n_hi - n_lo) * spread, n_hi + (n_hi - n_lo) * spread), 1)
        phosphorus = round(rand_in(p_lo - (p_hi - p_lo) * spread, p_hi + (p_hi - p_lo) * spread), 1)
        potassium = round(rand_in(k_lo - (k_hi - k_lo) * spread, k_hi + (k_hi - k_lo) * spread), 1)
        ph = round(rand_in(ph_lo - 0.5, ph_hi + 0.5), 1)
        temperature = round(rand_in(temp_lo - 3, temp_hi + 3), 1)
        rainfall = round(rand_in(rain_lo - 150, rain_hi + 150), 1)
        humidity = round(rand_in(humid_lo - 10, humid_hi + 10), 1)

    # Clamp to physically plausible ranges
    nitrogen = clamp(nitrogen, 0, 200)
    phosphorus = clamp(phosphorus, 0, 150)
    potassium = clamp(potassium, 0, 250)
    ph = clamp(ph, 3.5, 9.0)
    temperature = clamp(temperature, 10, 45)
    rainfall = clamp(rainfall, 100, 3000)
    humidity = clamp(humidity, 10, 100)

    # Pick crop-appropriate soil type
    preferred_soils = crop_req.get('soil_types', SOIL_TYPES)
    if random.random() < 0.8:
        soil_type = random.choice(preferred_soils)
    else:
        soil_type = random.choice(SOIL_TYPES)

    crop_variety = random.choice(CROP_VARIETIES.get(crop_name, ['Unknown']))
    farm_size = round(random.uniform(0.2, 10.0), 1)

    pest_type = random.choice(PEST_TYPES_BY_CROP.get(crop_name, ['None']))
    pest_severity = 'None' if pest_type == 'None' else random.choice(['Low', 'Moderate', 'High'])

    rainfall_var = random.choice(RAINFALL_VARIABILITY)
    temp_stress = random.choice(TEMPERATURE_STRESS)
    extreme = random.choices(EXTREME_WEATHER, weights=[70, 10, 15, 5])[0]
    labor = random.choice(LABOR_INPUT)
    fertilizer_type = random.choice(FERTILIZER_TYPES)
    fertilizer_amount = round(random.uniform(0, 200), 1) if fertilizer_type != 'None' else 0
    irrigation = random.choice(IRRIGATION_TYPES)
    soil_deg = random.choice(SOIL_DEGRADATION)

    # Generate yield
    yield_val = generate_yield(
        crop_req, nitrogen, phosphorus, potassium, ph,
        rainfall, temperature, humidity, pest_severity, farm_size
    )

    return {
        'region': region,
        'state': state,
        'agro_zone': zone_name,
        'crop_type': crop_name,
        'crop_variety': crop_variety,
        'soil_type': soil_type,
        'farm_size_ha': farm_size,
        'soil_pH': ph,
        'soil_nitrogen': nitrogen,
        'soil_phosphorus': phosphorus,
        'soil_potassium': potassium,
        'rainfall_mm': rainfall,
        'temperature_C': temperature,
        'fertilizer_type': fertilizer_type,
        'fertilizer_amount_kg_ha': fertilizer_amount,
        'irrigation_type': irrigation,
        'pest_type': pest_type,
        'pest_severity': pest_severity,
        'rainfall_variability': rainfall_var,
        'temperature_stress': temp_stress,
        'extreme_weather': extreme,
        'labor_input': labor,
        'soil_degradation': soil_deg,
        'yield_kg_ha': yield_val,
        'humidity': round(humidity, 1),
    }


def main():
    random.seed(RANDOM_SEED)

    # Load crop requirements
    with open(REQUIREMENTS_PATH, 'r') as f:
        crop_reqs = json.load(f)

    # Distribution weights (roughly matching Nigerian production volume)
    crop_weights = {
        'cassava': 0.18,
        'maize': 0.15,
        'rice': 0.12,
        'sorghum': 0.13,
        'yam': 0.14,
        'beans': 0.10,
        'tomato': 0.06,
        'pepper': 0.06,
        'onions': 0.06,
    }

    # Generate records
    records = []
    for i in range(NUM_RECORDS):
        # Weighted random crop selection
        crop_name = random.choices(
            list(crop_weights.keys()),
            weights=list(crop_weights.values()),
            k=1
        )[0]

        crop_req = crop_reqs[crop_name]
        display_name = crop_name.capitalize()
        record = generate_record(display_name, crop_req, i)
        records.append(record)

    # Write CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH) or '.', exist_ok=True)
    fieldnames = list(records[0].keys())

    with open(OUTPUT_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {NUM_RECORDS} records -> {OUTPUT_PATH}")

    # Print summary stats
    from collections import Counter, defaultdict
    crop_counts = Counter(r['crop_type'] for r in records)
    crop_yields = defaultdict(list)
    for r in records:
        crop_yields[r['crop_type']].append(r['yield_kg_ha'])

    print(f"\n{'Crop':<12} {'Count':>6} {'Avg Yield':>12} {'pH Range':>12} {'N Range':>12} {'Rain Range':>14}")
    print("-" * 72)
    for crop in sorted(crop_counts.keys()):
        crop_data = [r for r in records if r['crop_type'] == crop]
        avg_yield = sum(r['yield_kg_ha'] for r in crop_data) / len(crop_data)
        ph_min = min(r['soil_pH'] for r in crop_data)
        ph_max = max(r['soil_pH'] for r in crop_data)
        n_min = min(r['soil_nitrogen'] for r in crop_data)
        n_max = max(r['soil_nitrogen'] for r in crop_data)
        rain_min = min(r['rainfall_mm'] for r in crop_data)
        rain_max = max(r['rainfall_mm'] for r in crop_data)
        print(f"{crop:<12} {crop_counts[crop]:>6} {avg_yield:>10.0f}  {ph_min:>4.1f}-{ph_max:<4.1f} {n_min:>5.0f}-{n_max:<5.0f} {rain_min:>6.0f}-{rain_max:<6.0f}")


if __name__ == '__main__':
    main()
