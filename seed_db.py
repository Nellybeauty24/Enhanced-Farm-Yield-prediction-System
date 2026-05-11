"""
Database seeding script.
Populates the prediction_history table with realistic historical data
spanning the last 12 months across multiple crop types.

Usage:
    python seed_db.py
"""

import random
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.prediction import PredictionHistory

# Realistic crop profiles: (crop, base_yield_kgha, n_range, p_range, k_range, ph_range, temp_range, rainfall_range)
CROP_PROFILES = [
    {
        "crop": "Maize",
        "base_yield": 4200,
        "yield_variance": 800,
        "nitrogen": (60, 140),
        "phosphorus": (30, 80),
        "potassium": (40, 100),
        "ph": (5.8, 7.0),
        "temperature": (18, 32),
        "humidity": (50, 80),
        "rainfall": (500, 1200),
        "weight": 0.28
    },
    {
        "crop": "Rice",
        "base_yield": 3900,
        "yield_variance": 700,
        "nitrogen": (80, 160),
        "phosphorus": (20, 60),
        "potassium": (30, 80),
        "ph": (5.5, 7.0),
        "temperature": (20, 35),
        "humidity": (65, 95),
        "rainfall": (1200, 2500),
        "weight": 0.22
    },
    {
        "crop": "Cassava",
        "base_yield": 4600,
        "yield_variance": 900,
        "nitrogen": (20, 60),
        "phosphorus": (10, 40),
        "potassium": (80, 200),
        "ph": (5.5, 7.0),
        "temperature": (22, 34),
        "humidity": (60, 80),
        "rainfall": (800, 2000),
        "weight": 0.18
    },
    {
        "crop": "Wheat",
        "base_yield": 3800,
        "yield_variance": 600,
        "nitrogen": (40, 120),
        "phosphorus": (20, 70),
        "potassium": (30, 90),
        "ph": (6.0, 7.5),
        "temperature": (12, 22),
        "humidity": (40, 65),
        "rainfall": (375, 875),
        "weight": 0.15
    },
    {
        "crop": "Sorghum",
        "base_yield": 3600,
        "yield_variance": 700,
        "nitrogen": (40, 100),
        "phosphorus": (20, 60),
        "potassium": (30, 80),
        "ph": (5.5, 7.5),
        "temperature": (22, 38),
        "humidity": (35, 65),
        "rainfall": (300, 800),
        "weight": 0.12
    },
    {
        "crop": "Beans",
        "base_yield": 2800,
        "yield_variance": 500,
        "nitrogen": (10, 40),
        "phosphorus": (40, 100),
        "potassium": (30, 80),
        "ph": (6.0, 7.0),
        "temperature": (16, 28),
        "humidity": (45, 70),
        "rainfall": (400, 900),
        "weight": 0.05
    },
]


def rand_in(range_tuple, decimals=1):
    """Return a random float within the given range, rounded to `decimals` places."""
    val = random.uniform(range_tuple[0], range_tuple[1])
    return round(val, decimals)


def weighted_choice(profiles):
    """Pick a crop profile by weight."""
    total = sum(p["weight"] for p in profiles)
    r = random.uniform(0, total)
    cumulative = 0
    for p in profiles:
        cumulative += p["weight"]
        if r <= cumulative:
            return p
    return profiles[-1]


def generate_records(n=80):
    """Generate n realistic PredictionHistory records over the last 12 months."""
    records = []
    now = datetime.utcnow()
    twelve_months_ago = now - timedelta(days=365)

    for _ in range(n):
        profile = weighted_choice(CROP_PROFILES)

        # Spread timestamps over the past 12 months with slight clustering toward recent
        days_ago = int(random.betavariate(1.5, 2.5) * 365)
        timestamp = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

        nitrogen = rand_in(profile["nitrogen"])
        phosphorus = rand_in(profile["phosphorus"])
        potassium = rand_in(profile["potassium"])
        ph = rand_in(profile["ph"])
        temperature = rand_in(profile["temperature"])
        humidity = rand_in(profile["humidity"])
        rainfall = rand_in(profile["rainfall"], decimals=0)

        # Yield influenced by soil quality: higher N+P+K and optimal pH = better yield
        nutrient_score = (nitrogen / 140 + phosphorus / 80 + potassium / 100) / 3
        ph_optimal = 1 - abs(ph - 6.5) / 2  # Best at 6.5
        yield_modifier = (nutrient_score * 0.6 + ph_optimal * 0.4)
        predicted_yield = round(
            profile["base_yield"] * yield_modifier + random.uniform(-profile["yield_variance"] * 0.3, profile["yield_variance"] * 0.3),
            2
        )
        predicted_yield = max(500, predicted_yield)  # Floor at 500 kg/ha

        confidence = round(random.uniform(0.72, 0.98), 4)

        record = PredictionHistory(
            timestamp=timestamp,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph=ph,
            humidity=humidity,
            temperature=temperature,
            rainfall=rainfall,
            recommended_crop=profile["crop"],
            confidence=confidence,
            predicted_yield=predicted_yield,
            yield_unit='kg/ha'
        )
        records.append(record)
    return records


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        existing_count = PredictionHistory.query.count()
        print(f"  Existing records: {existing_count}")

        if existing_count >= 50:
            answer = input(f"  Database already has {existing_count} records. Add more? [y/N]: ").strip().lower()
            if answer != 'y':
                print("  Seeding skipped.")
                return

        print("  Generating 80 historical prediction records...")
        records = generate_records(n=80)
        db.session.bulk_save_objects(records)
        db.session.commit()

        final_count = PredictionHistory.query.count()
        print(f"  Seeding complete. Total records: {final_count}")
        
        # Print a quick summary
        from sqlalchemy import func
        summary = db.session.query(
            PredictionHistory.recommended_crop,
            func.count(PredictionHistory.id).label('count'),
            func.avg(PredictionHistory.predicted_yield).label('avg_yield')
        ).group_by(PredictionHistory.recommended_crop)\
         .order_by(func.count(PredictionHistory.id).desc())\
         .all()
        
        print("\n  Crop Distribution:")
        print(f"  {'Crop':<12} {'Count':>6} {'Avg Yield (kg/ha)':>20}")
        print(f"  {'-'*12} {'-'*6} {'-'*20}")
        for row in summary:
            avg = f"{row.avg_yield:.0f}" if row.avg_yield else "N/A"
            print(f"  {row.recommended_crop:<12} {row.count:>6} {avg:>20}")


if __name__ == '__main__':
    main()
