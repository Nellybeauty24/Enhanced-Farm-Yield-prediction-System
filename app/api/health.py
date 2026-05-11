"""
Health check and status endpoints.
Used for monitoring service health and model status.
"""

from flask import jsonify, Blueprint
from datetime import datetime
import logging
import sys

health_bp = Blueprint('health', __name__)
from ..services import CropPredictionService

logger = logging.getLogger(__name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    
    Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-24T10:30:00Z"
        }
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with model status and system info.
    
    Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-24T10:30:00Z",
            "service": {
                "name": "Soil Nutrition Prediction API",
                "version": "1.0.0"
            },
            "model": {
                "loaded": true,
                "type": "RandomForestClassifier",
                "has_probability": true
            },
            "system": {
                "python_version": "3.9.7"
            }
        }
    """
    try:
        # Get model information
        crop_service = CropPredictionService()
        model_info = crop_service.get_model_info()
        
        # Determine overall health status
        overall_status = "healthy" if model_info['loaded'] else "degraded"
        status_code = 200 if model_info['loaded'] else 503
        
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "service": {
                "name": "Soil Nutrition Prediction API",
                "version": "1.0.0",
                "api_version": "v1"
            },
            "model": {
                "loaded": model_info['loaded'],
                "type": model_info['model_type'],
                "has_probability": model_info['has_probability']
            },
            "system": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            }
        }
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "error": "Health check failed"
        }), 503


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 only if the service is ready to accept requests (model loaded).
    
    Response:
        {
            "ready": true,
            "timestamp": "2026-01-24T10:30:00Z"
        }
    """
    try:
        crop_service = CropPredictionService()
        model_info = crop_service.get_model_info()
        
        is_ready = model_info['loaded']
        status_code = 200 if is_ready else 503
        
        return jsonify({
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), status_code
        
    except Exception as e:
        logger.error(f"Error in readiness check: {str(e)}", exc_info=True)
        return jsonify({
            "ready": False,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the application process is alive.
    
    Response:
        {
            "alive": true,
            "timestamp": "2026-01-24T10:30:00Z"
        }
    """
    return jsonify({
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }), 200