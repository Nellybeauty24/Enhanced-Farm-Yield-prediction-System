import pandas as pd
import numpy as np
import os


def enhance_dataset(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Reading dataset from {input_path}...")
    df = pd.read_csv(input_path)

    # Mapping of agro-zones to base humidity ranges
    # Values inspired by typical Nigerian climate zones
    zone_humidity_map = {
        "Humid Forest": (70, 95),
        "Derived Savanna": (60, 85),
        "Northern Guinea Savanna": (45, 75),
        "Sudan Savanna": (35, 65),
        "Sahel Savanna": (25, 55),
    }

    print("Synthesizing humidity column...")

    def calculate_humidity(row):
        zone = row.get("agro_zone", "Unknown")
        rainfall = row.get("rainfall_mm", 1000)

        # Get base range or default if unknown
        base_min, base_max = zone_humidity_map.get(zone, (50, 80))

        # Add a factor based on rainfall (higher rainfall = higher humidity)
        # Assuming 2000mm is "high" rainfall for this dataset
        rainfall_factor = (rainfall / 2000.0) * 10

        # Generate random humidity within the range
        humidity = np.random.uniform(base_min, base_max) + rainfall_factor

        # Clamp to 0-100 range
        return min(max(humidity, 0), 100)

    # Set seed for reproducibility
    np.random.seed(42)
    df["humidity"] = df.apply(calculate_humidity, axis=1)

    print(f"Saving enhanced dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Dataset enhancement complete.")


if __name__ == "__main__":
    DATA_PATH = "data/nigeria_agri_yield_cleaned.csv"
    OUTPUT_PATH = "data/nigeria_agri_yield_enhanced.csv"
    enhance_dataset(DATA_PATH, OUTPUT_PATH)
