"""
Crop Prediction Service
Handles ML model loading, prediction logic, and probability calculation.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging
from catboost import CatBoostRegressor, CatBoostClassifier
from ..utils.features import compute_crop_features_from_input

logger = logging.getLogger(__name__)

class CropPredictionService:
    """Service for predicting suitable crops based on soil and environmental data."""
    
    _instance = None
    _model = None
    _yield_model = None
    _model_loaded = False
    _yield_model_loaded = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one model is loaded in memory."""
        if cls._instance is None:
            cls._instance = super(CropPredictionService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the service and load the model if not already loaded."""
        if not self._model_loaded:
            self._load_model()
        if not self._yield_model_loaded:
            self._load_yield_model()
    
    def _load_model(self) -> None:
        """
        Load the trained CatBoost crop classification model.
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, 'models', 'crop_model.cbm')
            
            if not os.path.exists(model_path):
                logger.error(f"Crop model file NOT FOUND at {model_path}")
                self._model_loaded = False
                return

            self._model = CatBoostClassifier()
            self._model.load_model(model_path)
            
            self._model_loaded = True
            logger.info(f"Crop model successfully loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load crop model: {str(e)}")
            self._model_loaded = False

    def _load_yield_model(self) -> None:
        """
        Load the trained CatBoost yield prediction model.
        """
        try:
            # Try implementing fallback paths
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_path, 'models', 'catboost_model.cbm')
            
            if not os.path.exists(model_path):
                 # Try relative to app root if absolute fails
                 model_path = 'models/catboost_model.cbm'
            
            if os.path.exists(model_path):
                self._yield_model = CatBoostRegressor()
                self._yield_model.load_model(model_path)
                self._yield_model_loaded = True
                logger.info(f"Yield model successfully loaded from {model_path}")
            else:
                logger.warning(f"Yield model file not found at {model_path}")
                raise Exception(f"Yield model file not found at {model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load yield model: {str(e)}")
            raise Exception(f"Failed to load yield model: {str(e)}")
    
    def predict(self, input_data: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict the most suitable crop based on input parameters.
        
        Args:
            input_data: Dictionary containing:
                - nitrogen (float): Nitrogen content in soil
                - phosphorus (float): Phosphorus content in soil
                - potassium (float): Potassium content in soil
                - ph (float): pH level of soil
                - temperature (float): Temperature in Celsius
                - rainfall (float): Rainfall in mm
        
        Returns:
            Tuple[str, float]: (predicted_crop, confidence_probability)
        
        Raises:
            ValueError: If input data is invalid
            Exception: If prediction fails
        """
        try:
            # Validate model is loaded
            if not self._model_loaded or self._model is None:
                raise Exception("Model not loaded. Cannot perform prediction.")
            
            # Extract raw inputs
            nitrogen = input_data['nitrogen']
            phosphorus = input_data['phosphorus']
            potassium = input_data['potassium']
            rainfall = input_data['rainfall']
            temperature = input_data['temperature']
            ph = input_data['ph']
            
            # Use shared feature engineering module
            engineered = compute_crop_features_from_input(
                nitrogen, phosphorus, potassium, ph, temperature, rainfall
            )

            # Build input DataFrame matching training feature order
            df_input = pd.DataFrame([{
                'agro_zone': input_data.get('agro_zone', 'Unknown'),
                'soil_type': input_data.get('soil_type', 'Unknown'),
                'soil_nitrogen': nitrogen,
                'soil_phosphorus': phosphorus,
                'soil_potassium': potassium,
                'soil_pH': ph,
                'temperature_C': temperature,
                'rainfall_mm': rainfall,
                'humidity': input_data.get('humidity', 60.0),
                **engineered
            }])
            
            # Make prediction with probabilities
            probs = self._model.predict_proba(df_input)[0]
            classes = self._model.classes_
            
            # Sort and get Top 3
            top_indices = np.argsort(probs)[::-1][:3]
            top_crops = [
                {
                    "crop": str(classes[i]),
                    "probability": float(probs[i])
                } 
                for i in top_indices
            ]
            
            # Use the best one for default legacy support
            recommended_crop = top_crops[0]["crop"]
            probability = top_crops[0]["probability"]

            return {
                "recommended_crop": recommended_crop,
                "probability": probability,
                "top_recommendations": top_crops # NEW: Full list for Top-3 UI
            }
            
        except ValueError as e:
            logger.warning(f"Invalid input data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise Exception(f"Prediction error: {str(e)}")

    def predict_yield(self, input_data: Dict[str, any]) -> float:
        """
        Predict crop yield based on soil and environmental data.
        
        Args:
            input_data: Dictionary containing crop_type and soil parameters
            
        Returns:
            float: Predicted yield in kg/ha
        """
        try:
            if not self._yield_model_loaded or self._yield_model is None:
                # Try loading again
                self._load_yield_model()
                if not self._yield_model_loaded:
                    raise Exception("Yield prediction model not loaded.")

            nitrogen = input_data.get('nitrogen')
            phosphorus = input_data.get('phosphorus')
            potassium = input_data.get('potassium')
            ph = input_data.get('ph')
            rainfall = input_data.get('rainfall')
            temperature = input_data.get('temperature')

            sfi = nitrogen + phosphorus + potassium
            npr = nitrogen / (phosphorus + 1e-6)
            ci = rainfall * temperature

            # All possible feature values keyed by the column name used during training
            data_dict = {
                'region': input_data.get('region', 'Unknown'),
                'state': input_data.get('state', 'Unknown'),
                'agro_zone': input_data.get('agro_zone', 'Unknown'),
                'crop_type': input_data.get('crop_type', 'Unknown'),
                'crop_variety': input_data.get('crop_variety', 'Unknown'),
                'soil_type': input_data.get('soil_type', 'Unknown'),
                'farm_size_ha': input_data.get('farm_size_ha', 1.0),
                'soil_pH': ph,
                'soil_nitrogen': nitrogen,
                'soil_phosphorus': phosphorus,
                'soil_potassium': potassium,
                'rainfall_mm': rainfall,
                'temperature_C': temperature,
                'fertilizer_type': input_data.get('fertilizer_type', 'NPK'),
                'fertilizer_amount_kg_ha': input_data.get('fertilizer_amount_kg_ha', 100.0),
                'irrigation_type': input_data.get('irrigation_type', 'Rainfed'),
                'pest_type': input_data.get('pest_type', 'None'),
                'pest_severity': input_data.get('pest_severity', 'None'),
                'rainfall_variability': input_data.get('rainfall_variability', 'Normal'),
                'temperature_stress': input_data.get('temperature_stress', 'None'),
                'extreme_weather': input_data.get('extreme_weather', 'None'),
                'labor_input': input_data.get('labor_input', 'Medium'),
                'soil_degradation': input_data.get('soil_degradation', 'None'),
                'humidity': input_data.get('humidity', 60.0),
                'soil_fertility_index': sfi,
                'np_ratio': npr,
                'climate_index': ci,
            }

            # Determine cat feature names from the model (by name, not positional index)
            model_feature_names = getattr(self._yield_model, 'feature_names_', None)
            cat_idxs = self._yield_model.get_cat_feature_indices() if hasattr(self._yield_model, 'get_cat_feature_indices') else []
            cat_feature_names = set()
            if model_feature_names and cat_idxs:
                cat_feature_names = {model_feature_names[i] for i in cat_idxs}

            if model_feature_names:
                # Build DataFrame in the exact column order the model was trained on
                row = {}
                for feat in model_feature_names:
                    if feat in data_dict:
                        val = data_dict[feat]
                    else:
                        val = 'Unknown' if feat in cat_feature_names else 0.0
                    row[feat] = str(val) if feat in cat_feature_names else val
                df_input = pd.DataFrame([row])[list(model_feature_names)]
            else:
                # Fallback: build DataFrame from data_dict and convert cat features by name
                df_input = pd.DataFrame([data_dict])
                for col in cat_feature_names:
                    if col in df_input.columns:
                        df_input[col] = df_input[col].astype(str)

            prediction = self._yield_model.predict(df_input)[0]
            
            logger.info(f"Yield prediction successful: {prediction:.2f} kg/ha")
            return float(prediction)

        except Exception as e:
            logger.error(f"Yield prediction failed: {str(e)}")
            raise Exception(f"Yield prediction error: {str(e)}")

    
    def _extract_features(self, input_data: Dict[str, float]) -> np.ndarray:
        """
        Extract and order features for model input.
        
        Args:
            input_data: Raw input dictionary
        
        Returns:
            numpy array of features in correct order
        """
        # Standard feature order for crop prediction models (matching training script)
        feature_order = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'rainfall']
        
        features = []
        for feature in feature_order:
            if feature not in input_data:
                raise ValueError(f"Missing required feature: {feature}")
            features.append(float(input_data[feature]))
        
        return np.array(features)
    
    def _validate_features(self, features: np.ndarray, input_data: Dict[str, float]) -> None:
        """
        Validate feature values are within acceptable ranges.
        
        Args:
            features: Feature array
            input_data: Original input data for detailed error messages
        
        Raises:
            ValueError: If any feature is out of valid range
        """
        validations = {
            'nitrogen': (0, 140, input_data['nitrogen']),
            'phosphorus': (5, 145, input_data['phosphorus']),
            'potassium': (5, 205, input_data['potassium']),
            'ph': (0, 14, input_data['ph']),
            'temperature': (-10, 50, input_data['temperature']),
            'rainfall': (0, 3000, input_data['rainfall'])
        }
        
        for param, (min_val, max_val, value) in validations.items():
            if not min_val <= value <= max_val:
                raise ValueError(
                    f"{param} value {value} is out of valid range [{min_val}, {max_val}]"
                )
    
    def _get_prediction_probability(self, features: np.ndarray) -> float:
        """
        Get prediction confidence/probability.
        
        Args:
            features: Feature array
        
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # If model supports predict_proba (e.g., RandomForest, SVM with probability=True)
            if hasattr(self._model, 'predict_proba'):
                probabilities = self._model.predict_proba([features])[0]
                return float(np.max(probabilities))
            
            # If model has decision_function (e.g., SVM)
            elif hasattr(self._model, 'decision_function'):
                decision = self._model.decision_function([features])[0]
                # Convert to probability-like score using sigmoid
                if isinstance(decision, np.ndarray):
                    decision = np.max(decision)
                probability = 1 / (1 + np.exp(-decision))
                return float(probability)
            
            # Default: return moderate confidence
            else:
                logger.warning("Model doesn't support probability calculation. Returning default.")
                return 0.75
                
        except Exception as e:
            logger.warning(f"Could not calculate probability: {str(e)}. Returning default.")
            return 0.75
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'loaded': self._model_loaded,
            'model_type': type(self._model).__name__ if self._model else None,
            'has_probability': hasattr(self._model, 'predict_proba') if self._model else False
        }