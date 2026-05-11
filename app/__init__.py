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

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Soil Nutrition Prediction API is running'}, 200

    return app
