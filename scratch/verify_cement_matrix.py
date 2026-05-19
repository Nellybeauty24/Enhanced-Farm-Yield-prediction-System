from scripts.generate_dataset import calculate_suitability
import json

with open('data/crop_requirements.json', 'r') as f:
    crop_reqs = json.load(f)

# Cement Matrix
nitrogen = 60
phosphorus = 40
potassium = 50
ph = 6.0
temperature = 26.0
rainfall = 1300
humidity = 70
agro_zone = 'Derived Savanna'
soil_type = 'Clay'

print(f"Calculating suitability under the Cement Matrix (Rainfall: {rainfall}mm, Soil: {soil_type}):")
for crop_name in ['tomato', 'pepper', 'maize', 'yam']:
    crop_req = crop_reqs[crop_name]
    compat = calculate_suitability(
        crop_name, crop_req, nitrogen, phosphorus, potassium, ph,
        rainfall, temperature, humidity, soil_type, agro_zone
    )
    print(f"  {crop_name.capitalize()}: {compat:.4f}")
