import pandas as pd
import json
import os

def generate_requirements():
    data_path = '../data/nigeria_agri_yield_cleaned-updated.xlsx'
    output_path = '../data/crop_requirements.json'
    
    # Ensure paths work whether run from scripts dir or project root
    if not os.path.exists(data_path):
        data_path = 'data/nigeria_agri_yield_cleaned-updated.xlsx'
        output_path = 'data/crop_requirements.json'
    
    print(f"Loading data from {data_path}...")
    df = pd.read_excel(data_path)
    
    requirements = {}
    
    crops = df['crop_type'].unique()
    print(f"Found {len(crops)} crops: {crops}")
    
    for crop in crops:
        crop_name = str(crop).lower()
        
        # Filter data to this crop
        crop_df = df[df['crop_type'] == crop]
        
        # We only want to look at the 'optimal' conditions, 
        # so let's focus on the top 25% of highest yielding records.
        if len(crop_df) > 10:
            yield_threshold = crop_df['yield_kg_ha'].quantile(0.75)
            optimal_df = crop_df[crop_df['yield_kg_ha'] >= yield_threshold]
        else:
            # Not enough data to filter safely, use all
            optimal_df = crop_df
            
        if len(optimal_df) == 0:
            continue
            
        # Extract the IQR (25th and 75th percentile) for parameters to provide a safe "optimal range"
        # We use percentiles instead of MIN/MAX to avoid extreme outliers.
        reqs = {
            'ph': (
                round(optimal_df['soil_pH'].quantile(0.25), 1),
                round(optimal_df['soil_pH'].quantile(0.75), 1)
            ),
            'nitrogen': (
                int(optimal_df['soil_nitrogen'].quantile(0.25)),
                int(optimal_df['soil_nitrogen'].quantile(0.75))
            ),
            'phosphorus': (
                int(optimal_df['soil_phosphorus'].quantile(0.25)),
                int(optimal_df['soil_phosphorus'].quantile(0.75))
            ),
            'potassium': (
                int(optimal_df['soil_potassium'].quantile(0.25)),
                int(optimal_df['soil_potassium'].quantile(0.75))
            ),
            'temperature': (
                int(optimal_df['temperature_C'].quantile(0.25)),
                int(optimal_df['temperature_C'].quantile(0.75))
            ),
            'rainfall': (
                int(optimal_df['rainfall_mm'].quantile(0.25)),
                int(optimal_df['rainfall_mm'].quantile(0.75))
            )
        }
        
        requirements[crop_name] = reqs
        print(f"Successfully generated requirements for {crop_name}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(requirements, f, indent=4)
        
    print(f"\nSaved requirements to {output_path}")

if __name__ == '__main__':
    generate_requirements()
