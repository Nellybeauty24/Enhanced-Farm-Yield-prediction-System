from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 

    # Register Blueprints
    from app.api import api_v1

    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # Eagerly load ML models during application startup to prevent I/O bottlenecks and race conditions
    with app.app_context():
        try:
            from app.services import CropPredictionService
            app.logger.info("Eagerly initializing CropPredictionService to pre-load CatBoost models...")
            CropPredictionService()
        except Exception as e:
            app.logger.error(f"Failed to eagerly load ML models during startup: {str(e)}")

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Soil Nutrition Prediction API is running'}, 200

    return app
