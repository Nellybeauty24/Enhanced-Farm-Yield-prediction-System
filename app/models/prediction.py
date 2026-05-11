from datetime import datetime
from .. import db

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # allow nullable for guests, or not? The plan says anonymous guests might be supported. If strictly required later, we can change to nullable=False.
    
    # Input Features
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    rainfall = db.Column(db.Float, nullable=True)
    
    # Prediction Results
    recommended_crop = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    
    # For yield predictions
    predicted_yield = db.Column(db.Float, nullable=True)
    yield_unit = db.Column(db.String(20), nullable=True, default='kg/ha')
    
    # User Profile & Geo-Location Data
    state = db.Column(db.String(100), nullable=True)
    local_gov = db.Column(db.String(100), nullable=True)
    plot_size = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    
    # Post-Harvest Tracking
    actual_yield = db.Column(db.Float, nullable=True)
    
    # New simulation context fields
    region = db.Column(db.String(100), nullable=True)
    agro_zone = db.Column(db.String(100), nullable=True)
    soil_type = db.Column(db.String(100), nullable=True)
    pest_type = db.Column(db.String(100), nullable=True)
    pest_severity = db.Column(db.String(100), nullable=True)
    rainfall_variability = db.Column(db.String(100), nullable=True)
    labor_input = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'ph': self.ph,
            'humidity': self.humidity,
            'temperature': self.temperature,
            'recommended_crop': self.recommended_crop,
            'confidence': self.confidence,
            'predicted_yield': self.predicted_yield,
            'yield_unit': self.yield_unit,
            'state': self.state,
            'local_gov': self.local_gov,
            'plot_size': self.plot_size,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'actual_yield': self.actual_yield,
            'region': self.region,
            'agro_zone': self.agro_zone,
            'soil_type': self.soil_type,
            'pest_type': self.pest_type,
            'pest_severity': self.pest_severity,
            'rainfall_variability': self.rainfall_variability,
            'labor_input': self.labor_input
        }
