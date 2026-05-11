"""
Prediction API endpoints.
Handles crop prediction requests and returns recommendations.
"""

from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from datetime import datetime, timedelta
import logging

prediction_bp = Blueprint('prediction', __name__)
from .. import db
from ..services import CropPredictionService, RecommendationService
from ..models.prediction import PredictionHistory
from ..schemas.prediction_schema import (
    PredictionInputSchema, PredictionOutputSchema, 
    YieldPredictionInputSchema, YieldPredictionOutputSchema,
    PredictionSaveSchema
)
from ..utils.exceptions import ModelNotLoadedError, PredictionError, InvalidInputError
from .auth import require_auth

logger = logging.getLogger(__name__)

# Initialize services
crop_service = CropPredictionService()
recommendation_service = RecommendationService()

# Initialize schemas
input_schema = PredictionInputSchema()
output_schema = PredictionOutputSchema()
yield_input_schema = YieldPredictionInputSchema()
yield_output_schema = YieldPredictionOutputSchema()


@prediction_bp.route('/predict', methods=['POST'])
@require_auth
def predict_crop(current_user):
    """
    Predict suitable crop based on soil nutrition and environmental data.
    """
    try:
        # Get JSON data from request
        if not request.is_json:
            raise InvalidInputError("Request must be JSON")
        
        input_data = request.get_json()
        
        # Validate input using Marshmallow schema
        try:
            validated_data = input_schema.load(input_data)
        except ValidationError as err:
            logger.warning(f"Validation error: {err.messages}")
            return jsonify({
                "status": "error",
                "message": "Invalid input data",
                "errors": err.messages,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Make prediction
        try:
            prediction_result = crop_service.predict(validated_data)
            predicted_crop = prediction_result['recommended_crop']
            confidence = prediction_result['probability']
            top_recommendations = prediction_result['top_recommendations']
        except ValueError as e:
            logger.error(f"Value error during prediction: {str(e)}")
            raise InvalidInputError(str(e))
        except Exception as e:
            logger.error(f"Prediction service error: {str(e)}")
            raise PredictionError(f"Failed to generate prediction: {str(e)}")
        
        # Generate recommendations
        try:
            recommendations = recommendation_service.generate_recommendations(
                predicted_crop,
                validated_data,
                confidence
            )
        except Exception as e:
            logger.error(f"Recommendation service error: {str(e)}")
            recommendations = [
                "Unable to generate detailed recommendations. Please consult with an agricultural expert."
            ]
        
        # Prepare response
        response_data = {
            "recommended_crop": str(predicted_crop),
            "probability": round(float(confidence), 4),
            "top_recommendations": top_recommendations,
            "recommendations": recommendations,
            "input_summary": {
                "nitrogen": validated_data['nitrogen'],
                "phosphorus": validated_data['phosphorus'],
                "potassium": validated_data['potassium'],
                "ph": validated_data['ph']
            }
        }
        
        # Removed database persistence here to fulfill Explicit Save constraint
            
        # Validate output
        validated_output = output_schema.dump(response_data)
        
        # Return successful response
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": validated_output
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.messages}")
        return jsonify({
            "status": "error",
            "message": "Invalid input data",
            "errors": e.messages,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 400
        
    except InvalidInputError as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 400
        
    except (ModelNotLoadedError, PredictionError) as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in predict endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@prediction_bp.route('/predict-yield', methods=['POST'])
def predict_yield():
    """
    Predict crop yield based on soil nutrition and environmental data.
    """
    try:
        request_data = request.get_json()
        if not request_data:
            raise InvalidInputError("No input data provided")
            
        validated_data = yield_input_schema.load(request_data)
        prediction = crop_service.predict_yield(validated_data)
        predicted_yield_rounded = round(float(prediction), 2)
        
        response_data = {
            "predicted_yield": predicted_yield_rounded,
            "unit": "kg/ha",
            "confidence_interval": None,
            "input_summary": validated_data
        }
        
        validated_output = yield_output_schema.dump(response_data)
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": validated_output
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Validation Error",
            "errors": e.messages,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 400
    except InvalidInputError as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 400
    except Exception as e:
        logger.error(f"Error in predict-yield endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@prediction_bp.route('/predict/batch', methods=['POST'])
def predict_crop_batch():
    return jsonify({"status": "error", "message": "Batch operations temporarily disabled."}), 400


@prediction_bp.route('/crops/<crop_name>/requirements', methods=['GET'])
def get_crop_requirements(crop_name):
    try:
        requirements = recommendation_service.get_optimal_ranges(crop_name)
        if requirements is None:
            return jsonify({
                "status": "error",
                "message": f"No data available for crop: {crop_name}",
                "available_crops": list(recommendation_service.CROP_REQUIREMENTS.keys()),
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": {
                "crop": crop_name.lower(),
                "description": "Optimal soil and environmental ranges calculated from the top 25% highest-yielding historical harvests in the dataset.",
                "units": {
                    "nitrogen": "mg/kg (ppm) or kg/ha depending on local soil test standards",
                    "phosphorus": "mg/kg (ppm) or kg/ha",
                    "potassium": "mg/kg (ppm) or kg/ha",
                    "ph": "Standard pH scale (0-14)",
                    "temperature": "Celsius (°C)",
                    "rainfall": "mm per season/year"
                },
                "requirements": requirements
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching crop requirements: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve crop requirements",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@prediction_bp.route('/crops', methods=['GET'])
def list_available_crops():
    try:
        crops = list(recommendation_service.CROP_REQUIREMENTS.keys())
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "data": {
                "crops": sorted(crops),
                "total": len(crops)
            }
        }), 200
    except Exception as e:
        logger.error(f"Error listing crops: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve available crops",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@prediction_bp.route('/predict/save', methods=['POST'])
@require_auth
def save_prediction(current_user):
    """
    Explicitly save a prediction record with demographic, geographic, and simulation data.
    """
    try:
        if not request.is_json:
            raise InvalidInputError("Request must be JSON")
            
        input_data = request.get_json()
        schema = PredictionSaveSchema()
        try:
            validated_data = schema.load(input_data)
        except ValidationError as err:
            return jsonify({
                "status": "error",
                "message": "Invalid input data",
                "errors": err.messages,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
            
        # --- DUPLICATE CHECK ---
        # Check if an identical prediction was saved by this user in the last 5 minutes
        time_threshold = datetime.utcnow() - timedelta(minutes=5)
        existing_duplicate = PredictionHistory.query.filter(
            PredictionHistory.user_id == current_user.id,
            PredictionHistory.nitrogen == validated_data['nitrogen'],
            PredictionHistory.phosphorus == validated_data['phosphorus'],
            PredictionHistory.potassium == validated_data['potassium'],
            PredictionHistory.ph == validated_data['ph'],
            PredictionHistory.timestamp >= time_threshold
        ).first()

        if existing_duplicate:
            return jsonify({
                "status": "error",
                "message": "Duplicate submission: You have already saved an identical prediction in the last 5 minutes.",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 409 # Conflict
            
        # Build the record
        record = PredictionHistory(
            nitrogen=validated_data['nitrogen'],
            phosphorus=validated_data['phosphorus'],
            potassium=validated_data['potassium'],
            ph=validated_data['ph'],
            humidity=validated_data.get('humidity'),
            temperature=validated_data.get('temperature'),
            rainfall=validated_data.get('rainfall'),
            recommended_crop=validated_data['recommended_crop'],
            confidence=validated_data['confidence'],
            state=validated_data['state'],
            local_gov=validated_data['local_gov'],
            plot_size=validated_data['plot_size'],
            longitude=validated_data['longitude'],
            latitude=validated_data['latitude'],
            predicted_yield=validated_data['predicted_yield'],
            actual_yield=validated_data.get('actual_yield'),
            region=validated_data.get('region'),
            agro_zone=validated_data.get('agro_zone'),
            soil_type=validated_data.get('soil_type'),
            pest_type=validated_data.get('pest_type'),
            pest_severity=validated_data.get('pest_severity'),
            rainfall_variability=validated_data.get('rainfall_variability'),
            labor_input=validated_data.get('labor_input'),
            user_id=current_user.id,
            yield_unit='kg/ha'
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Complete prediction profile saved successfully",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 201
        
    except InvalidInputError as e:
        return jsonify({"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat() + 'Z'}), 400
    except Exception as e:
        logger.error(f"Error in save_prediction: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server error: {str(e)}", "timestamp": datetime.utcnow().isoformat() + 'Z'}), 500

@prediction_bp.route('/predict/<int:prediction_id>/actual-yield', methods=['PATCH'])
@require_auth
def update_actual_yield(current_user, prediction_id):
    """
    Update the actual harvest yield of a specific historical prediction.
    """
    try:
        if not request.is_json:
            raise InvalidInputError("Request must be JSON")
            
        input_data = request.get_json()
        if 'actual_yield' not in input_data:
            return jsonify({
                "status": "error",
                "message": "Missing 'actual_yield' field",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 400
            
        record = PredictionHistory.query.get(prediction_id)
        if not record:
            return jsonify({
                "status": "error",
                "message": "Prediction record not found",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404
            
        if record.user_id != current_user.id:
            return jsonify({
                "status": "error",
                "message": "Unauthorized: You do not own this record",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 403
            
        record.actual_yield = float(input_data['actual_yield'])
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Actual yield recorded successfully",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except ValueError:
        return jsonify({"status": "error", "message": "actual_yield must be a valid number", "timestamp": datetime.utcnow().isoformat() + 'Z'}), 400
    except Exception as e:
        logger.error(f"Error updating actual yield: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Server error: {str(e)}", "timestamp": datetime.utcnow().isoformat() + 'Z'}), 500
