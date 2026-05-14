import pandas as pd
import os
import sys
import numpy as np
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, classification_report

# File paths
DATA_PATH = 'data/nigeria_agri_yield_enhanced.csv'
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'crop_model.cbm')

def engineer_features(df):
    """Advanced feature engineering including interactions."""
    print("Engineering high-dimensional features...")
    # 1. Base indices
    df['soil_fertility_index'] = df['soil_nitrogen'] + df['soil_phosphorus'] + df['soil_potassium']
    df['np_ratio'] = df['soil_nitrogen'] / (df['soil_phosphorus'] + 1e-6)
    df['climate_index'] = df['rainfall_mm'] * df['temperature_C']
    df['ph_stress'] = (df['soil_pH'] - 7.0).abs()
    
    # 2. Interactions (Non-linear relationships)
    df['n_ph_inter'] = df['soil_nitrogen'] * df['soil_pH']
    df['p_ph_inter'] = df['soil_phosphorus'] * df['soil_pH']
    
    # Moisture vs Heat stress
    df['rain_temp_ratio'] = df['rainfall_mm'] / (df['temperature_C'] + 1e-6)
    
    return df

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print(f"Warning: {DATA_PATH} not found, falling back to original.")
        DATA_PATH_ORIG = 'data/nigeria_agri_yield_cleaned.csv'
        if os.path.exists(DATA_PATH_ORIG):
            df = pd.read_csv(DATA_PATH_ORIG)
            # Synthesize humidity on the fly if not present
            if 'humidity' not in df.columns:
                 print("Synthesizing humidity on the fly...")
                 df['humidity'] = np.random.uniform(40, 90, size=len(df))
        else:
            print("Error: Dataset not found!")
            return
    else:
        df = pd.read_csv(DATA_PATH)

    df = engineer_features(df)

    categorical_features = [
        'agro_zone', 'soil_type'
    ]
    
    numeric_features = [
        'soil_nitrogen', 'soil_phosphorus', 'soil_potassium', 
        'soil_pH', 'temperature_C', 'rainfall_mm', 'humidity',
        'soil_fertility_index', 'np_ratio', 'climate_index', 'ph_stress',
        'n_ph_inter', 'p_ph_inter', 'rain_temp_ratio'
    ]
    
    target_col = 'crop_type'
    df_clean = df[categorical_features + numeric_features + [target_col]].dropna()

    X = df_clean[categorical_features + numeric_features]
    y = df_clean[target_col]

    # SPLIT FIRST to avoid data leakage
    X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Class weights for balance
    classes = np.unique(y_train_full)
    weights = len(y_train_full) / (len(classes) * pd.Series(y_train_full).value_counts().sort_index().values)
    class_weights = dict(zip(classes, weights))

    print("\nStarting Fast Training...")
    best_params = {'depth': 6, 'learning_rate': 0.1, 'l2_leaf_reg': 3}
    
    # Train final model on ALL training data
    final_model = CatBoostClassifier(
        iterations=500,
        depth=best_params['depth'],
        learning_rate=best_params['learning_rate'],
        l2_leaf_reg=best_params['l2_leaf_reg'],
        loss_function='MultiClass',
        cat_features=categorical_features,
        class_weights=class_weights,
        random_seed=42,
        verbose=100
    )
    final_model.fit(X_train_full, y_train_full)

    # EVALUATE ON TRULY UNSEEN TEST SET
    y_pred = final_model.predict(X_test)
    print("\nFinal Classification Report (Unseen Test Data):")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    final_model.save_model(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
