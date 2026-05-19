import json
from scripts.generate_dataset import calculate_suitability

with open('data/crop_requirements.json', 'r') as f:
    crop_reqs = json.load(f)

# UI parameters
nitrogen = 85
phosphorus = 40
potassium = 60
ph = 6.5
temperature = 32.5
rainfall = 650
humidity = 44.9
agro_zone = 'Sudan Savanna'
soil_type = 'Loamy'

print("Calculating compatibility for each crop under UI conditions:")
for crop_name, crop_req in crop_reqs.items():
    compat = calculate_suitability(
        crop_name, crop_req, nitrogen, phosphorus, potassium, ph,
        rainfall, temperature, humidity, soil_type, agro_zone
    )
    print(f"  {crop_name.capitalize()}: {compat:.4f}")
