"""
API package initialization.
Registers all blueprints for the application.
"""

from flask import Blueprint

# Create API blueprint with v1 prefix
api_v1 = Blueprint('api_v1', __name__)

# Import routes after blueprint creation to avoid circular imports
from .health import health_bp
from .analytics import analytics_bp
from .prediction import prediction_bp
from .auth import auth_bp

api_v1.register_blueprint(analytics_bp, url_prefix='/analytics')
api_v1.register_blueprint(prediction_bp)
api_v1.register_blueprint(health_bp)
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
