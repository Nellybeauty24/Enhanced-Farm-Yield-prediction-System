import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from catboost import CatBoostRegressor, Pool

# File path
DATA_PATH = 'data/nigeria_agri_yield_cleaned-updated.xlsx'

def load_and_inspect_data(filepath):
    """
    Loads data from Excel, prints inspection info, and validates target column.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
        
    try:
        print(f"Loading data from {filepath}...")
        df = pd.read_excel(filepath)
        
        # Print dataset shape
        print(f"\nDataset Shape: {df.shape}")
        
        # Print column names
        print(f"\nColumn Names:\n{df.columns.tolist()}")
        
        # Print missing value count
        print(f"\nMissing Values:\n{df.isnull().sum()}")
        
        # Print basic statistics
        print(f"\nBasic Statistics:\n{df.describe()}")
        
        # Ensure target column exists
        target_col = 'yield_kg_ha'
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset.")
            
        print(f"\nSuccess: Target column '{target_col}' exists.")
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        raise e

def engineer_features(df):
    """
    Adds engineered features:
    - soil_fertility_index
    - np_ratio
    - climate_index
    """
    print("\nEngineering features...")
    try:
        # soil_fertility_index = nitrogen + phosphorus + potassium
        df['soil_fertility_index'] = df['soil_nitrogen'] + df['soil_phosphorus'] + df['soil_potassium']
        
        # np_ratio = nitrogen / (phosphorus + 1e-6) to avoid division by zero
        df['np_ratio'] = df['soil_nitrogen'] / (df['soil_phosphorus'] + 1e-6)
        
        # climate_index = rainfall_mm * temperature_C
        df['climate_index'] = df['rainfall_mm'] * df['temperature_C']
        
        print("New features added: ['soil_fertility_index', 'np_ratio', 'climate_index']")
        print(f"New Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error during feature engineering: {e}")
        raise e

def prepare_data(df):
    """
    Separates X and y.
    Identifies categorical and numeric columns.
    """
    print("\nPreparing data...")
    target_col = 'yield_kg_ha'
    
    if target_col not in df.columns:
         raise ValueError(f"Target column '{target_col}' not found.")

    # Separate X and y
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Identify categorical columns (dtype object)
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    
    # Identify numeric columns (number)
    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()
    
    with open('data_prep_info.txt', 'w') as f:
        f.write(f"Target Variable: {target_col}\n")
        f.write(f"Features Shape: {X.shape}\n")
        f.write(f"Target Shape: {y.shape}\n")
        
        f.write(f"\nCategorical Columns ({len(categorical_cols)}):\n")
        f.write(f"{categorical_cols}\n")
        
        f.write(f"\nNumeric Columns ({len(numeric_cols)}):\n")
        f.write(f"{numeric_cols}\n")

    print(f"Target Variable: {target_col}")
    print(f"Features Shape: {X.shape}")
    print(f"Target Shape: {y.shape}")
    
    print(f"\nCategorical Columns ({len(categorical_cols)}):")
    print(categorical_cols)
    
    print(f"\nNumeric Columns ({len(numeric_cols)}):")
    print(numeric_cols)
    
    return X, y, categorical_cols, numeric_cols

def setup_cv(X, y, stratification_col):
    """
    Creates StratifiedKFold object.
    """
    print("\nSetting up Stratified K-Fold...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    print(f"StratifiedKFold created: n_splits=5, shuffle=True, random_state=42")
    
    # Verify splits generation (printing first fold stats)
    print(f"Stratification column: {stratification_col.name}")
    
    return skf

def train_cv_loop(X, y, skf, cat_features, stratification_col):
    """
    Runs Cross-Validation loop.
    Returns metrics and out-of-fold predictions.
    """
    print("\nStarting Cross-Validation Loop...")
    
    fold_metrics = []
    oof_preds = np.zeros(len(X))
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, stratification_col)):
        print(f"\nFold {fold + 1}...")
        
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        # Initialize CatBoostRegressor
        model = CatBoostRegressor(
            iterations=500,
            learning_rate=0.05,
            depth=6,
            loss_function='RMSE',
            eval_metric='RMSE',
            random_seed=42,
            cat_features=cat_features,
            verbose=100,
            early_stopping_rounds=150
        )
        
        # Train model
        model.fit(
            X_train, y_train,
            eval_set=(X_val, y_val),
            use_best_model=True
        )
        
        # Predict
        preds = model.predict(X_val)
        oof_preds[val_idx] = preds
        
        # Calculate Metrics
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        mae = mean_absolute_error(y_val, preds)
        r2 = r2_score(y_val, preds)
        mape = mean_absolute_percentage_error(y_val, preds)
        
        print(f"Fold {fold + 1} Metrics: RMSE={rmse:.4f}, MAE={mae:.4f}, R2={r2:.4f}, MAPE={mape:.4f}")
        
        fold_metrics.append({
            'fold': fold + 1,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mape': mape
        })
        
    return fold_metrics, oof_preds

def train_final_model(X, y, cat_features):
    """
    Trains model on full dataset and saves it.
    """
    print("\nTraining Final Model on Full Dataset...")
    
    model = CatBoostRegressor(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        loss_function='RMSE',
        eval_metric='RMSE',
        random_seed=42,
        cat_features=cat_features,
        verbose=100
    )
    
    model.fit(X, y)
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    model_path = 'models/catboost_model.cbm'
    model.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    return model

def extract_and_plot_importance(model, feature_names):
    """
    Extracts feature importance and plots top 20 features.
    """
    print("\nExtracting Feature Importance...")
    
    importance = model.get_feature_importance()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values(by='importance', ascending=False)
    
    # Save to CSV
    importance_df.to_csv('outputs/feature_importance.csv', index=False)
    print("Feature importance saved to outputs/feature_importance.csv")
    
    # Plot Top 20
    plt.figure(figsize=(10, 8))
    top_20 = importance_df.head(20).sort_values(by='importance', ascending=True)
    
    plt.barh(top_20['feature'], top_20['importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.title('Top 20 Feature Importance')
    plt.tight_layout()
    
    plt.savefig('outputs/feature_importance.png')
    print("Feature importance plot saved to outputs/feature_importance.png")
    
    return importance_df

def generate_shap_plots(model, X):
    """
    Generates SHAP summary plot for 1000 random samples.
    """
    print("\nGenerating SHAP Plots...")
    
    # Select 1000 random samples
    if len(X) > 1000:
        X_sample = X.sample(1000, random_state=42)
    else:
        X_sample = X
        
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    plt.savefig('outputs/shap_summary.png')
    plt.close()
    
    print("SHAP summary plot saved to outputs/shap_summary.png")

if __name__ == "__main__":
    try:
        df = load_and_inspect_data(DATA_PATH)
        df = engineer_features(df)
        
        X, y, cat_features, num_features = prepare_data(df)
        
        # Stratify by crop_type
        if 'crop_type' not in X.columns:
             raise ValueError("crop_type column not found in Features.")
             
        skf = setup_cv(X, y, X['crop_type'])
        
        metrics, oof_preds = train_cv_loop(X, y, skf, cat_features, X['crop_type'])
        
        print("\nTraining Complete.")
        
        # Create metrics DataFrame
        metrics_df = pd.DataFrame(metrics)
        
        # Calculate Mean and Std
        mean_metrics = metrics_df[['rmse', 'mae', 'r2', 'mape']].mean()
        std_metrics = metrics_df[['rmse', 'mae', 'r2', 'mape']].std()
        
        print("\nFold-wise Metrics:")
        print(metrics_df)
        
        print("\nFinal Average Metrics:")
        print(f"RMSE: {mean_metrics['rmse']:.4f} ± {std_metrics['rmse']:.4f}")
        print(f"MAE:  {mean_metrics['mae']:.4f} ± {std_metrics['mae']:.4f}")
        print(f"R2:   {mean_metrics['r2']:.4f} ± {std_metrics['r2']:.4f}")
        print(f"MAPE: {mean_metrics['mape']:.4f} ± {std_metrics['mape']:.4f}")
        
        # Ensure outputs directory exists
        os.makedirs('outputs', exist_ok=True)
        
        # Save results
        metrics_df.to_csv('outputs/cv_results.csv', index=False)
        print("\nResults saved to outputs/cv_results.csv")
        
        # Train and Save Final Model
        final_model = train_final_model(X, y, cat_features)
        
        # Extract and Plot Feature Importance
        extract_and_plot_importance(final_model, X.columns.tolist())
        
        # Generate SHAP Plots
        generate_shap_plots(final_model, X)
        
    except Exception as e:
        sys.exit(1)
