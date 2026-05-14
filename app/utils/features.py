"""
Shared Feature Engineering Module.
Centralizes all feature engineering logic to prevent divergence between
training scripts and the production prediction service.
"""


def engineer_crop_features(df):
    """
    Engineer features for crop classification model.
    Must be called with a DataFrame containing the base columns.

    Args:
        df: pandas DataFrame with columns:
            soil_nitrogen, soil_phosphorus, soil_potassium,
            soil_pH, rainfall_mm, temperature_C

    Returns:
        DataFrame with additional engineered columns.
    """
    df = df.copy()
    df['soil_fertility_index'] = df['soil_nitrogen'] + df['soil_phosphorus'] + df['soil_potassium']
    df['np_ratio'] = df['soil_nitrogen'] / (df['soil_phosphorus'] + 1e-6)
    df['climate_index'] = df['rainfall_mm'] * df['temperature_C']
    df['ph_stress'] = (df['soil_pH'] - 7.0).abs()

    # Interaction features
    df['n_ph_inter'] = df['soil_nitrogen'] * df['soil_pH']
    df['p_ph_inter'] = df['soil_phosphorus'] * df['soil_pH']
    df['rain_temp_ratio'] = df['rainfall_mm'] / (df['temperature_C'] + 1e-6)

    return df


def engineer_yield_features(df):
    """
    Engineer features for yield regression model.

    Args:
        df: pandas DataFrame with columns:
            soil_nitrogen, soil_phosphorus, soil_potassium,
            rainfall_mm, temperature_C

    Returns:
        DataFrame with additional engineered columns.
    """
    df = df.copy()
    df['soil_fertility_index'] = df['soil_nitrogen'] + df['soil_phosphorus'] + df['soil_potassium']
    df['np_ratio'] = df['soil_nitrogen'] / (df['soil_phosphorus'] + 1e-6)
    df['climate_index'] = df['rainfall_mm'] * df['temperature_C']

    return df


def compute_crop_features_from_input(nitrogen, phosphorus, potassium, ph, temperature, rainfall):
    """
    Compute engineered feature values from raw input scalars.
    Used by CropPredictionService to avoid DataFrame overhead for single predictions.

    Returns:
        dict of engineered feature values
    """
    return {
        'soil_fertility_index': nitrogen + phosphorus + potassium,
        'np_ratio': nitrogen / (phosphorus + 1e-6),
        'climate_index': rainfall * temperature,
        'ph_stress': abs(ph - 7.0),
        'n_ph_inter': nitrogen * ph,
        'p_ph_inter': phosphorus * ph,
        'rain_temp_ratio': rainfall / (temperature + 1e-6),
    }
