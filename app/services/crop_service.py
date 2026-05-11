"""
Crop Prediction Service
Handles ML model loading, prediction logic, and probability calculation.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging
from catboost import CatBoostRegressor, CatBoostClassifier

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
                # Fallback to old pickle model if cbm doesn't exist yet
                old_path = os.path.join(base_dir, 'models', 'crop_model.pkl')
                if os.path.exists(old_path):
                    with open(old_path, 'rb') as f:
                        self._model = pickle.load(f)
                    self._model_loaded = True
                    return
                
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
            
            # Feature engineering for the high-performance model
            nitrogen = input_data['nitrogen']
            phosphorus = input_data['phosphorus']
            potassium = input_data['potassium']
            rainfall = input_data['rainfall']
            temperature = input_data['temperature']
            ph = input_data['ph']
            
            sfi = nitrogen + phosphorus + potassium
            npr = nitrogen / (phosphorus + 1e-6)
            ci = rainfall * temperature
            ph_stress = abs(ph - 7.0)
            
            # NEW: Interaction features from the 57% accuracy sprint
            n_ph_inter = nitrogen * ph
            p_ph_inter = phosphorus * ph
            rain_temp_ratio = rainfall / (temperature + 1e-6)

            # Extract features in the EXACT order used in train_crop_model.py
            df_input = pd.DataFrame([{
                'region': input_data.get('region', 'Unknown'),
                'state': input_data.get('state', 'Unknown'),
                'agro_zone': input_data.get('agro_zone', 'Unknown'),
                'soil_type': input_data.get('soil_type', 'Unknown'),
                'pest_type': input_data.get('pest_type', 'None'),
                'pest_severity': input_data.get('pest_severity', 'Low'),
                'rainfall_variability': input_data.get('rainfall_variability', 'Medium'),
                'labor_input': input_data.get('labor_input', 'Medium'),
                'soil_nitrogen': nitrogen,
                'soil_phosphorus': phosphorus,
                'soil_potassium': potassium,
                'soil_pH': ph,
                'temperature_C': temperature,
                'rainfall_mm': rainfall,
                'farm_size_ha': input_data.get('farm_size_ha', 1.0),
                'soil_fertility_index': sfi,
                'np_ratio': npr,
                'climate_index': ci,
                'ph_stress': ph_stress,
                'n_ph_inter': n_ph_inter,
                'p_ph_inter': p_ph_inter,
                'rain_temp_ratio': rain_temp_ratio
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

            # Prepare features for CatBoost
            # Feature mapping based on training data columns
            features = {
                'nitrogen': input_data.get('nitrogen'),
                'phosphorus': input_data.get('phosphorus'),
                'potassium': input_data.get('potassium'),
                'ph': input_data.get('ph'),
                'rainfall': input_data.get('rainfall'),
                'temperature': input_data.get('temperature'),
                'crop_type': input_data.get('crop_type'),
                'crop_variety': input_data.get('crop_variety', 'Unknown'),
                'soil_type': input_data.get('soil_type', 'Unknown'),
                'region': input_data.get('region', 'Unknown'),
                'state': input_data.get('state', 'Unknown'),
                'agro_zone': input_data.get('agro_zone', 'Unknown'),
                'farm_size_ha': input_data.get('farm_size_ha', 1.0),
                'labor_input': input_data.get('labor_input', 'Medium'),
                'rainfall_variability': input_data.get('rainfall_variability', 'Medium'),
                'pest_severity': input_data.get('pest_severity', 'Low'),
                'pest_type': input_data.get('pest_type', 'None')
            }
            
            # We need to calculate engineered features:
            sfi = features['nitrogen'] + features['phosphorus'] + features['potassium']
            npr = features['nitrogen'] / (features['phosphorus'] + 1e-6)
            ci = features['rainfall'] * features['temperature']
            
            # Map robustly using Pandas DataFrame with exact column names from training
            df_input = pd.DataFrame([{
                'region': features['region'],
                'state': features['state'],
                'agro_zone': features['agro_zone'],
                'crop_type': features['crop_type'],
                'crop_variety': features['crop_variety'],
                'soil_type': features['soil_type'],
                'farm_size_ha': features['farm_size_ha'],
                'soil_pH': features['ph'],
                'soil_nitrogen': features['nitrogen'],
                'soil_phosphorus': features['phosphorus'],
                'soil_potassium': features['potassium'],
                'rainfall_mm': features['rainfall'],
                'temperature_C': features['temperature'],
                'pest_type': features['pest_type'],
                'pest_severity': features['pest_severity'],
                'rainfall_variability': features['rainfall_variability'],
                'labor_input': features['labor_input'],
                'soil_fertility_index': sfi,
                'np_ratio': npr,
                'climate_index': ci
            }])

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