"""
Dataset Generator for Enhanced Farm Yield Prediction System.
Generates a biologically consistent synthetic dataset where environmental features
determine the crop class label (competitive suitability under Liebig's Law).

Usage:
    python scripts/generate_dataset.py
"""

import csv
import json
import random
import os
import math
import numpy as np

OUTPUT_PATH = 'data/nigeria_agri_yield_enhanced.csv'
REQUIREMENTS_PATH = 'data/crop_requirements.json'
NUM_RECORDS = 20000
RANDOM_SEED = 42

# Nigerian Geographic Data
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
LABOR_INPUT = ['Low', 'Medium', 'High']


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def get_parameter_score(val, lo, hi, is_nutrient=False, crop_name=None, param_name=None):
    if lo <= val <= hi:
        return 1.0
    if val < lo:
        ratio = val / lo
        return max(0.0, ratio ** 3)  # Cubic penalty for starvation floor
    else:
        if is_nutrient:
            # Nutrient exceedance plateaus at 1.0 (luxury consumption)
            # Apply a mild penalty for extreme Nitrogen surpluses in fruiting/bulb crops (vegetative locking)
            if param_name == 'nitrogen' and crop_name in ['tomato', 'pepper', 'onions'] and val > hi * 1.5:
                return 0.8  # Vegetative lock penalty
            return 1.0
        else:
            ratio = hi / val
            return max(0.0, ratio ** 1.5)  # Less severe penalty for exceedance


LETHAL_TEMPERATURE_LIMITS = {
    'rice': (15.0, 38.0),
    'cassava': (15.0, 37.0),
    'yam': (16.0, 36.0),
    'maize': (10.0, 35.0),
    'sorghum': (15.0, 43.0),
    'beans': (10.0, 30.0),
    'onions': (8.0, 30.0),
    'tomato': (10.0, 31.0),
    'pepper': (12.0, 35.0)
}


def calculate_suitability(crop_name, crop_req, nitrogen, phosphorus, potassium, ph, rainfall, temperature, humidity, soil_type, agro_zone):
    if agro_zone not in crop_req['agro_zones']:
        return 0.0

    # 1. Enforce hard physiological/lethal survival limits
    c_name = crop_name.lower()
    t_min, t_max = LETHAL_TEMPERATURE_LIMITS[c_name]
    if temperature < t_min or temperature > t_max:
        return 0.0

    # Solanaceae drainage / root rot lethal threshold
    if c_name in ['tomato', 'pepper']:
        if soil_type == 'Clay' and rainfall > 1000.0:
            return 0.0

    # Onions: excess nitrogen inhibits bulbing ("thick neck" syndrome)
    if c_name == 'onions' and nitrogen > 80.0:
        return 0.0

    # Tomato: excess nitrogen inhibits fruit setting (forces leaf growth instead)
    if c_name == 'tomato' and nitrogen > 130.0:
        return 0.0

    n_score = get_parameter_score(nitrogen, *crop_req['nitrogen'], is_nutrient=True, crop_name=c_name, param_name='nitrogen')
    p_score = get_parameter_score(phosphorus, *crop_req['phosphorus'], is_nutrient=True, crop_name=c_name, param_name='phosphorus')
    k_score = get_parameter_score(potassium, *crop_req['potassium'], is_nutrient=True, crop_name=c_name, param_name='potassium')
    ph_score = get_parameter_score(ph, *crop_req['ph'])
    rain_score = get_parameter_score(rainfall, *crop_req['rainfall'])
    temp_score = get_parameter_score(temperature, *crop_req['temperature'])
    humid_score = get_parameter_score(humidity, *crop_req['humidity'])

    soil_score = 1.0 if soil_type in crop_req['soil_types'] else 0.5

    # Liebig's Law of the Minimum: plant growth is determined by the scarcest resource
    min_nutrient_score = min(n_score, p_score, k_score)
    min_env_score = min(ph_score, rain_score, temp_score, humid_score)
    
    compatibility = min(min_nutrient_score, min_env_score) * (0.8 + 0.2 * soil_score)

    # Solanaceae drainage stunting penalty for moderate rain in clayey soil
    if c_name in ['tomato', 'pepper'] and soil_type == 'Clay':
        compatibility *= 0.3

    return compatibility


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    with open(REQUIREMENTS_PATH, 'r') as f:
        crop_reqs = json.load(f)

    records = []
    print(f"Generating {NUM_RECORDS} biologically consistent records...")

    # We sample the environmental matrix first, then find the biological winner
    for i in range(NUM_RECORDS):
        while True:
            # 1. Agro-zone template selection
            zone_name = random.choices(
                ['Humid Forest', 'Derived Savanna', 'Northern Guinea Savanna', 'Sudan Savanna', 'Sahel Savanna'],
                weights=[0.25, 0.30, 0.25, 0.15, 0.05],
                k=1
            )[0]
            zone = AGRO_ZONE_CONFIG[zone_name]

            # 2. Regional and State mapping
            region = random.choice(zone['regions'])
            states = zone['states'][region]
            state = random.choice(states)

            # 3. Environment parameters: Continuous spectrum across Nigerian geography
            t_lo, t_hi = zone['base_temp']
            r_lo, r_hi = zone['base_rainfall']
            h_lo, h_hi = zone['base_humidity']

            temperature = round(clamp(random.uniform(t_lo - 2, t_hi + 2) + random.gauss(0, 0.5), 10, 45), 1)
            rainfall = round(clamp(random.uniform(r_lo - 100, r_hi + 100) + random.gauss(0, 20), 100, 3000), 1)
            humidity = round(clamp(random.uniform(h_lo - 5, h_hi + 5) + random.gauss(0, 2), 10, 100), 1)

            # Soil
            ph = round(clamp(random.uniform(4.0, 8.5) + random.gauss(0, 0.1), 3.5, 9.0), 1)
            soil_type = random.choice(SOIL_TYPES)

            # Nutrients
            nitrogen = round(clamp(random.uniform(5, 150) + random.gauss(0, 2), 0, 200), 1)
            phosphorus = round(clamp(random.uniform(5, 110) + random.gauss(0, 2), 0, 150), 1)
            potassium = round(clamp(random.uniform(15, 220) + random.gauss(0, 3), 0, 250), 1)

            # 4. Evaluate compatibility of all crops
            compatibilities = {}
            for crop_name, crop_req in crop_reqs.items():
                compatibilities[crop_name] = calculate_suitability(
                    crop_name, crop_req, nitrogen, phosphorus, potassium, ph,
                    rainfall, temperature, humidity, soil_type, zone_name
                )

            # Pick the biological winner (highest compatibility)
            best_crop = max(compatibilities, key=compatibilities.get)
            max_compat = compatibilities[best_crop]

            # If even the best crop has zero compatibility, re-sample to avoid dead spaces
            if max_compat > 0.05:
                break

        # 5. Populate crop attributes and yield for the winner
        display_crop_name = best_crop.capitalize()
        crop_req = crop_reqs[best_crop]

        # Additional operational attributes
        crop_variety = random.choice(CROP_VARIETIES[display_crop_name])

        fertilizer_type = random.choices(FERTILIZER_TYPES, weights=[50, 20, 15, 5, 10])[0]
        fertilizer_amount = round(random.uniform(20, 180), 1) if fertilizer_type != 'None' else 0.0
        
        irrigation = random.choices(IRRIGATION_TYPES, weights=[60, 15, 15, 5, 5])[0]

        # Yield generation tied directly to compatibility score + management factors
        base_yield = crop_req['base_yield']
        yield_variance = crop_req['yield_variance']

        # Path B: Deterministic Predictor using conditional risk mitigation
        # Regional base risk penalties (unmitigated aridity, leaching, etc.)
        ZONE_BASE_PENALTIES = {
            'Humid Forest': 0.05,
            'Derived Savanna': 0.10,
            'Northern Guinea Savanna': 0.15,
            'Sudan Savanna': 0.28,
            'Sahel Savanna': 0.40
        }
        base_penalty = ZONE_BASE_PENALTIES[zone_name]

        # Calculate mitigation efficiency based on zone and management inputs
        mitigation_efficiency = 0.0
        if zone_name in ['Sahel Savanna', 'Sudan Savanna']:
            if irrigation in ['Drip', 'Sprinkler']:
                mitigation_efficiency = 0.85  # Modern irrigation neutralizes 85% of aridity risk
            elif irrigation == 'Surface':
                mitigation_efficiency = 0.50  # Traditional irrigation neutralizes 50%
        elif zone_name in ['Northern Guinea Savanna', 'Derived Savanna']:
            if irrigation in ['Drip', 'Sprinkler']:
                mitigation_efficiency = 0.60
            elif irrigation == 'Surface':
                mitigation_efficiency = 0.30
        elif zone_name == 'Humid Forest':
            # Humid Forest risks are leaching/acidity. Organic manure/compost increases soil organic matter, 
            # buffering pH and improving Cation Exchange Capacity (CEC). 
            if fertilizer_type == 'Organic':
                mitigation_efficiency = 0.80  # Organic compost mitigates 80% of leaching/CEC degradation
            else:
                # NPK/Urea provide macronutrients (captured in fertilizer_bonus) 
                # but provide ZERO mitigation to the structural acidification/leaching penalty
                mitigation_efficiency = 0.0

        effective_risk_factor = 1.0 - (base_penalty * (1.0 - mitigation_efficiency))
        
        # Standard fertilizer bonus representing baseline biomass growth (applies globally)
        fertilizer_bonus = 1.15 if (fertilizer_type != 'None' and max_compat < 1.0) else 1.0

        yield_val = (
            base_yield * max_compat * 
            fertilizer_bonus * 
            effective_risk_factor
        )
        yield_val += random.gauss(0, yield_variance * 0.1)
        yield_val = max(100, round(yield_val, 1))

        records.append({
            'region': region,
            'state': state,
            'agro_zone': zone_name,
            'crop_type': display_crop_name,
            'crop_variety': crop_variety,
            'soil_type': soil_type,
            'soil_pH': ph,
            'soil_nitrogen': nitrogen,
            'soil_phosphorus': phosphorus,
            'soil_potassium': potassium,
            'rainfall_mm': rainfall,
            'temperature_C': temperature,
            'fertilizer_type': fertilizer_type,
            'fertilizer_amount_kg_ha': fertilizer_amount,
            'irrigation_type': irrigation,
            'yield_kg_ha': yield_val,
            'humidity': humidity
        })

    # Write CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH) or '.', exist_ok=True)
    fieldnames = list(records[0].keys())

    with open(OUTPUT_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\nGenerated {NUM_RECORDS} records -> {OUTPUT_PATH}")

    # Summary Stats
    from collections import Counter
    crop_counts = Counter(r['crop_type'] for r in records)
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
