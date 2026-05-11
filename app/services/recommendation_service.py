"""
Recommendation Service
Provides actionable agricultural recommendations based on soil conditions and predicted crop.
"""

from typing import Dict, List
import logging
import json
import os

logger = logging.getLogger(__name__)


def _load_crop_requirements() -> Dict[str, Dict[str, tuple]]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    req_path = os.path.join(base_dir, 'data', 'crop_requirements.json')
    try:
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                data = json.load(f)
                
            # Convert lists to tuples since JSON parses them as lists
            for crop, reqs in data.items():
                for param, tr in reqs.items():
                    reqs[param] = tuple(tr)
            
            logger.info(f"Loaded dynamic requirements for {len(data)} crops.")
            return data
    except Exception as e:
        logger.warning(f"Could not load dynamic crop requirements from {req_path}: {e}. Using fallback.")
    
    # Fallback to hardcoded requirements
    return {
        'rice': {
            'ph': (5.5, 7.0),
            'nitrogen': (40, 60),
            'phosphorus': (30, 50),
            'potassium': (30, 50),
            'temperature': (20, 30),
            'humidity': (70, 90),
            'rainfall': (150, 300)
        },
        'wheat': {
            'ph': (6.0, 7.5),
            'nitrogen': (40, 80),
            'phosphorus': (20, 40),
            'potassium': (20, 40),
            'temperature': (12, 25),
            'humidity': (50, 70),
            'rainfall': (50, 100)
        },
        'maize': {
            'ph': (5.5, 7.0),
            'nitrogen': (60, 100),
            'phosphorus': (40, 60),
            'potassium': (30, 60),
            'temperature': (18, 27),
            'humidity': (60, 80),
            'rainfall': (80, 150)
        },
        'cotton': {
            'ph': (5.5, 8.0),
            'nitrogen': (60, 120),
            'phosphorus': (30, 60),
            'potassium': (40, 80),
            'temperature': (21, 30),
            'humidity': (50, 70),
            'rainfall': (60, 120)
        },
        'sugarcane': {
            'ph': (6.0, 7.5),
            'nitrogen': (80, 120),
            'phosphorus': (40, 80),
            'potassium': (60, 100),
            'temperature': (20, 30),
            'humidity': (70, 90),
            'rainfall': (150, 250)
        },
        'coffee': {
            'ph': (6.0, 6.5),
            'nitrogen': (60, 100),
            'phosphorus': (30, 50),
            'potassium': (50, 80),
            'temperature': (15, 24),
            'humidity': (60, 80),
            'rainfall': (150, 200)
        }
    }

class RecommendationService:
    """Service for generating crop-specific and soil-specific recommendations."""
    
    # Optimal ranges for different crops
    CROP_REQUIREMENTS = _load_crop_requirements()
    
    def generate_recommendations(
        self, 
        predicted_crop: str, 
        input_data: Dict[str, float],
        confidence: float
    ) -> List[str]:
        """
        Generate actionable recommendations based on crop and soil conditions.
        
        Args:
            predicted_crop: The crop predicted by the model
            input_data: Soil and environmental parameters
            confidence: Prediction confidence score
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Normalize crop name
        crop = predicted_crop.lower()
        
        # Add confidence-based recommendation
        recommendations.extend(self._confidence_recommendations(confidence, crop))
        
        # Add crop-specific recommendations if we have data for this crop
        if crop in self.CROP_REQUIREMENTS:
            recommendations.extend(
                self._crop_specific_recommendations(crop, input_data)
            )
        else:
            # Generic recommendations for unknown crops
            recommendations.extend(self._generic_recommendations(input_data))
        
        # Add general soil health recommendations
        recommendations.extend(self._soil_health_recommendations(input_data))
        
        logger.info(f"Generated {len(recommendations)} recommendations for {predicted_crop}")
        
        return recommendations
    
    def _confidence_recommendations(self, confidence: float, crop: str) -> List[str]:
        """Generate recommendations based on prediction confidence."""
        recommendations = []
        
        if confidence < 0.6:
            recommendations.append(
                f"The prediction confidence for {crop.title()} is moderate ({confidence:.0%}). "
                "Consider consulting with a local agricultural expert for verification."
            )
            recommendations.append(
                "Soil testing by a certified laboratory is recommended to confirm nutrient levels."
            )
        elif confidence >= 0.85:
            recommendations.append(
                f"{crop.title()} is highly suitable for your soil conditions (confidence: {confidence:.0%})."
            )
        
        return recommendations
    
    def _crop_specific_recommendations(
        self, 
        crop: str, 
        input_data: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations specific to the predicted crop."""
        recommendations = []
        requirements = self.CROP_REQUIREMENTS[crop]
        
        # pH recommendations
        ph = input_data.get('ph', 7.0)
        ph_min, ph_max = requirements['ph']
        if ph < ph_min:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is too acidic for {crop.title()}. "
                f"Apply lime to raise pH to {ph_min}-{ph_max} range for optimal growth."
            )
        elif ph > ph_max:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is too alkaline for {crop.title()}. "
                f"Apply sulfur or organic matter to lower pH to {ph_min}-{ph_max} range."
            )
        else:
            recommendations.append(
                f"Soil pH ({ph:.1f}) is within the optimal range for {crop.title()}."
            )
        
        # Nitrogen recommendations
        n = input_data.get('nitrogen', 50.0)
        n_min, n_max = requirements['nitrogen']
        if n < n_min:
            deficit = n_min - n
            recommendations.append(
                f"Nitrogen levels are low. Apply approximately {deficit:.0f} kg/ha of "
                "nitrogen-rich fertilizer (urea or ammonium nitrate) before planting."
            )
        elif n > n_max:
            recommendations.append(
                f"Nitrogen levels are high ({n:.0f}). Avoid additional N fertilizers "
                "to prevent excessive vegetative growth and lodging."
            )
        
        # Phosphorus recommendations
        p = input_data.get('phosphorus', 40.0)
        p_min, p_max = requirements['phosphorus']
        if p < p_min:
            recommendations.append(
                f"Phosphorus is deficient. Apply phosphate fertilizers (DAP or SSP) "
                f"to raise levels by approximately {p_min - p:.0f} units."
            )
        
        # Potassium recommendations
        k = input_data.get('potassium', 40.0)
        k_min, k_max = requirements['potassium']
        if k < k_min:
            recommendations.append(
                f"Potassium is below optimal levels. Apply potash (MOP or SOP) "
                f"to increase by {k_min - k:.0f} units for better root development."
            )
        
        # Temperature recommendations
        temp = input_data.get('temperature', 25.0)
        temp_min, temp_max = requirements['temperature']
        if temp < temp_min:
            recommendations.append(
                f"Current temperature ({temp:.1f}°C) is below optimal for {crop.title()}. "
                f"Consider delaying planting until temperatures reach {temp_min}°C or higher."
            )
        elif temp > temp_max:
            recommendations.append(
                f"Temperature ({temp:.1f}°C) is high for {crop.title()}. "
                "Ensure adequate irrigation and consider shade netting if possible."
            )
        
        # Rainfall recommendations
        rainfall = input_data.get('rainfall', 100.0)
        rain_min, rain_max = requirements['rainfall']
        if rainfall < rain_min:
            recommendations.append(
                f"Rainfall ({rainfall:.0f}mm) is insufficient. Plan for supplementary "
                f"irrigation to meet the {rain_min}-{rain_max}mm requirement."
            )
        elif rainfall > rain_max:
            recommendations.append(
                f"Rainfall is high ({rainfall:.0f}mm). Ensure proper drainage to prevent "
                "waterlogging and root diseases."
            )
        
        return recommendations
    
    def _generic_recommendations(self, input_data: Dict[str, float]) -> List[str]:
        """Generate generic recommendations when crop-specific data is unavailable."""
        recommendations = []
        
        # Basic pH guidance
        ph = input_data.get('ph', 7.0)
        if ph < 5.5:
            recommendations.append("Soil is acidic. Consider liming to improve nutrient availability.")
        elif ph > 8.0:
            recommendations.append("Soil is alkaline. Organic matter can help balance pH.")
        
        # Basic nutrient guidance
        if input_data.get('nitrogen', 50.0) < 30:
            recommendations.append("Nitrogen levels are low. Add organic compost or nitrogen fertilizer.")
        
        if input_data.get('phosphorus', 40.0) < 20:
            recommendations.append("Phosphorus is deficient. Apply rock phosphate or bone meal.")
        
        if input_data.get('potassium', 40.0) < 20:
            recommendations.append("Potassium is low. Add wood ash or potassium fertilizer.")
        
        return recommendations
    
    def _soil_health_recommendations(self, input_data: Dict[str, float]) -> List[str]:
        """Generate general soil health recommendations."""
        recommendations = []
        
        # NPK balance check
        n = input_data.get('nitrogen', 0)
        p = input_data.get('phosphorus', 0)
        k = input_data.get('potassium', 0)
        
        # Check NPK ratio (ideal is roughly 4:2:1 for many crops)
        if n > 0 and p > 0 and k > 0:
            ratio_np = n / p if p > 0 else 0
            ratio_nk = n / k if k > 0 else 0
            
            if ratio_np > 5 or ratio_nk > 6:
                recommendations.append(
                    "NPK ratio is imbalanced. Consider soil testing and balanced fertilization "
                    "to optimize nutrient uptake."
                )
        
        # Humidity considerations
        humidity = input_data.get('humidity', 50.0)
        if humidity < 40:
            recommendations.append(
                "Low humidity detected. Mulching can help retain soil moisture and reduce evaporation."
            )
        elif humidity > 85:
            recommendations.append(
                "High humidity may increase disease risk. Ensure good air circulation and "
                "avoid overhead irrigation."
            )
        
        # General best practices
        recommendations.append(
            "Regular soil testing (annually or bi-annually) is recommended to monitor nutrient levels."
        )
        
        return recommendations
    
    def get_optimal_ranges(self, crop: str) -> Dict[str, tuple]:
        """
        Get optimal parameter ranges for a specific crop.
        
        Args:
            crop: Crop name (case-insensitive)
        
        Returns:
            Dictionary of parameter ranges or None if crop not found
        """
        crop_lower = crop.lower()
        return self.CROP_REQUIREMENTS.get(crop_lower, None)