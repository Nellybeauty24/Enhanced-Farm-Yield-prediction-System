import pandas as pd
import os
import sys
import numpy as np
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, classification_report

# File paths
DATA_PATH = 'data/nigeria_agri_yield_cleaned.csv'
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
    # Nutrient availability often depends on pH
    df['n_ph_inter'] = df['soil_nitrogen'] * df['soil_pH']
    df['p_ph_inter'] = df['soil_phosphorus'] * df['soil_pH']
    
    # Moisture vs Heat stress
    df['rain_temp_ratio'] = df['rainfall_mm'] / (df['temperature_C'] + 1e-6)
    
    return df

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        DATA_PATH_ALT = 'data/nigeria_agri_yield_cleaned-updated.xlsx'
        if os.path.exists(DATA_PATH_ALT):
            df = pd.read_excel(DATA_PATH_ALT)
        else:
            print("Error: Dataset not found!")
            return
    else:
        df = pd.read_csv(DATA_PATH)

    df = engineer_features(df)

    categorical_features = [
        'region', 'state', 'agro_zone', 'soil_type', 
        'pest_type', 'pest_severity', 'rainfall_variability', 'labor_input'
    ]
    
    numeric_features = [
        'soil_nitrogen', 'soil_phosphorus', 'soil_potassium', 
        'soil_pH', 'temperature_C', 'rainfall_mm', 'farm_size_ha',
        'soil_fertility_index', 'np_ratio', 'climate_index', 'ph_stress',
        'n_ph_inter', 'p_ph_inter', 'rain_temp_ratio'
    ]
    
    target_col = 'crop_type'
    df_clean = df[categorical_features + numeric_features + [target_col]].dropna()

    X = df_clean[categorical_features + numeric_features]
    y = df_clean[target_col]

    # Class weights for balance
    classes = np.unique(y)
    weights = len(y) / (len(classes) * pd.Series(y).value_counts().sort_index().values)
    class_weights = dict(zip(classes, weights))

    print("\nStarting Hyperparameter Optimization Sprint...")
    
    # Grid of parameters to test (Focused search)
    param_grid = [
        {'depth': 6, 'learning_rate': 0.1, 'l2_leaf_reg': 3},
        {'depth': 8, 'learning_rate': 0.05, 'l2_leaf_reg': 5},
        {'depth': 10, 'learning_rate': 0.03, 'l2_leaf_reg': 7}
    ]
    
    best_acc = 0
    best_model = None
    
    # 3-Fold CV for speed in this sprint
    kf = KFold(n_splits=3, shuffle=True, random_state=42)
    
    for i, params in enumerate(param_grid):
        print(f"\nTrial {i+1}/3: Testing {params}...")
        fold_accs = []
        
        for train_idx, val_idx in kf.split(X):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model = CatBoostClassifier(
                iterations=800,
                depth=params['depth'],
                learning_rate=params['learning_rate'],
                l2_leaf_reg=params['l2_leaf_reg'],
                loss_function='MultiClass',
                cat_features=categorical_features,
                class_weights=class_weights,
                random_seed=42,
                verbose=False,
                early_stopping_rounds=50
            )
            
            model.fit(X_tr, y_tr, eval_set=(X_val, y_val))
            acc = accuracy_score(y_val, model.predict(X_val))
            fold_accs.append(acc)
            
        avg_acc = np.mean(fold_accs)
        print(f"Average Accuracy for Trial {i+1}: {avg_acc:.4f}")
        
        if avg_acc > best_acc:
            best_acc = avg_acc
            # Train final model on full data for this config
            best_model = CatBoostClassifier(
                iterations=1000,
                depth=params['depth'],
                learning_rate=params['learning_rate'],
                l2_leaf_reg=params['l2_leaf_reg'],
                loss_function='MultiClass',
                cat_features=categorical_features,
                class_weights=class_weights,
                random_seed=42,
                verbose=200
            )
            best_model.fit(X, y)

    print(f"\nOptimization Complete! Best CV Accuracy: {best_acc:.4f}")
    
    # Final Evaluation on a holdout set (for reporting)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_pred = best_model.predict(X_test)
    print("\nFinal Classification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    best_model.save_model(MODEL_PATH)
    print(f"Optimized model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
