"""
Prediction validation schemas.
Defines request and response schemas for crop prediction endpoints.
"""

from marshmallow import Schema, fields, validates, validates_schema, ValidationError, EXCLUDE
from typing import Dict, Any


class PredictionInputSchema(Schema):
    """
    Schema for validating crop prediction input data.
    
    All fields represent soil nutrition and environmental parameters
    required for accurate crop prediction.
    """
    
    class Meta:
        # Exclude unknown fields instead of raising an error
        unknown = EXCLUDE
    
    nitrogen = fields.Float(
        required=True,
        error_messages={
            "required": "Nitrogen content is required",
            "invalid": "Nitrogen must be a valid number"
        }
    )
    
    phosphorus = fields.Float(
        required=True,
        error_messages={
            "required": "Phosphorus content is required",
            "invalid": "Phosphorus must be a valid number"
        }
    )
    
    potassium = fields.Float(
        required=True,
        error_messages={
            "required": "Potassium content is required",
            "invalid": "Potassium must be a valid number"
        }
    )
    
    ph = fields.Float(
        required=True,
        error_messages={
            "required": "pH level is required",
            "invalid": "pH must be a valid number"
        }
    )
    
    humidity = fields.Float(
        required=False,
        load_default=50.0,
        error_messages={
            "invalid": "Humidity must be a valid number"
        }
    )
    
    temperature = fields.Float(
        required=True,
        error_messages={
            "required": "Temperature is required",
            "invalid": "Temperature must be a valid number"
        }
    )
    
    rainfall = fields.Float(
        required=True,
        error_messages={
            "required": "Rainfall is required",
            "invalid": "Rainfall must be a valid number"
        }
    )
    
    # New features for enhanced accuracy
    region = fields.String(load_default="Unknown")
    state = fields.String(load_default="Unknown")
    agro_zone = fields.String(load_default="Unknown")
    soil_type = fields.String(load_default="Unknown")
    farm_size_ha = fields.Float(load_default=1.0)
    pest_type = fields.String(load_default="None")
    pest_severity = fields.String(load_default="Low")
    rainfall_variability = fields.String(load_default="Medium")
    labor_input = fields.String(load_default="Medium")
    
    @validates('nitrogen')
    def validate_nitrogen(self, value: float, **kwargs) -> None:
        """Validate nitrogen content is within acceptable range."""
        if value < 0:
            raise ValidationError("Nitrogen cannot be negative")
        if value > 140:
            raise ValidationError("Nitrogen value exceeds maximum expected range (0-140)")
    
    @validates('phosphorus')
    def validate_phosphorus(self, value: float, **kwargs) -> None:
        """Validate phosphorus content is within acceptable range."""
        if value < 0:
            raise ValidationError("Phosphorus cannot be negative")
        if value > 145:
            raise ValidationError("Phosphorus value exceeds maximum expected range (0-145)")
    
    @validates('potassium')
    def validate_potassium(self, value: float, **kwargs) -> None:
        """Validate potassium content is within acceptable range."""
        if value < 0:
            raise ValidationError("Potassium cannot be negative")
        if value > 205:
            raise ValidationError("Potassium value exceeds maximum expected range (0-205)")
    
    @validates('ph')
    def validate_ph(self, value: float, **kwargs) -> None:
        """Validate pH level is within valid range."""
        if value < 0:
            raise ValidationError("pH cannot be negative")
        if value > 14:
            raise ValidationError("pH cannot exceed 14 (maximum pH scale value)")
        # Warn about extreme values (though not invalid)
        if value < 3.5 or value > 10:
            # Note: This is just logged, not raised as error
            pass  # Could add warning logging here
    
    @validates('humidity')
    def validate_humidity(self, value: float, **kwargs) -> None:
        """Validate humidity is within valid percentage range."""
        if value < 0:
            raise ValidationError("Humidity cannot be negative")
        if value > 100:
            raise ValidationError("Humidity cannot exceed 100%")
    
    @validates('temperature')
    def validate_temperature(self, value: float, **kwargs) -> None:
        """Validate temperature is within reasonable range."""
        if value < -50:
            raise ValidationError("Temperature is unrealistically low (minimum: -50°C)")
        if value > 60:
            raise ValidationError("Temperature is unrealistically high (maximum: 60°C)")
    
    @validates('rainfall')
    def validate_rainfall(self, value: float, **kwargs) -> None:
        """Validate rainfall is within reasonable range."""
        if value < 0:
            raise ValidationError("Rainfall cannot be negative")
        if value > 5000:
            raise ValidationError("Rainfall value exceeds reasonable maximum (0-5000mm)")
    
    @validates_schema
    def validate_overall_data(self, data: Dict[str, Any], **kwargs) -> None:
        """
        Perform cross-field validation to ensure data consistency.
        
        Checks for logical inconsistencies across multiple fields.
        """
        # Check for unrealistic combinations
        temp = data.get('temperature', 0)
        humidity = data.get('humidity', 0)
        rainfall = data.get('rainfall', 0)
        
        # Very low rainfall with very high humidity is suspicious
        if rainfall < 20 and humidity > 90:
            # This is a warning case, not necessarily invalid
            # Could log this for monitoring
            pass
        
        # Very high temperature with very high humidity
        if temp > 40 and humidity > 95:
            # Extreme but possible in tropical regions
            pass
        
        # Extremely low nutrients across the board might indicate data issue
        n = data.get('nitrogen', 0)
        p = data.get('phosphorus', 0)
        k = data.get('potassium', 0)
        
        if n < 1 and p < 1 and k < 1:
            raise ValidationError(
                "All NPK values are near zero. Please verify soil test results."
            )


class PredictionOutputSchema(Schema):
    """
    Schema for validating crop prediction output data.
    Ensures consistent response format.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    recommended_crop = fields.String(
        required=True,
        error_messages={"required": "Recommended crop is required in response"}
    )
    
    probability = fields.Float(
        required=True,
        error_messages={"required": "Prediction probability is required in response"}
    )
    
    recommendations = fields.List(
        fields.String(),
        required=True,
        error_messages={"required": "Recommendations list is required in response"}
    )
    
    top_recommendations = fields.List(
        fields.Dict(),
        required=False
    )
    
    input_summary = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        required=False
    )
    
    id = fields.Integer(required=False)
    
    @validates('probability')
    def validate_probability(self, value: float, **kwargs) -> None:
        """Validate probability is between 0 and 1."""
        if value < 0 or value > 1:
            raise ValidationError("Probability must be between 0 and 1")
    
    @validates('recommended_crop')
    def validate_crop_name(self, value: str, **kwargs) -> None:
        """Validate crop name is not empty."""
        if not value or not value.strip():
            raise ValidationError("Crop name cannot be empty")
    
    @validates('recommendations')
    def validate_recommendations(self, value: list, **kwargs) -> None:
        """Validate recommendations list is not empty."""
        if not value:
            raise ValidationError("Recommendations list cannot be empty")
        if len(value) > 50:
            raise ValidationError("Too many recommendations (maximum: 50)")

class PredictionSaveSchema(Schema):
    """
    Schema for validating demographic, geographic, and full ML simulation data upon save.
    """
    class Meta:
        unknown = EXCLUDE
        
    nitrogen = fields.Float(required=True)
    phosphorus = fields.Float(required=True)
    potassium = fields.Float(required=True)
    ph = fields.Float(required=True)
    humidity = fields.Float(required=False)
    temperature = fields.Float(required=False)
    rainfall = fields.Float(required=False)
    
    recommended_crop = fields.String(required=True)
    confidence = fields.Float(required=True)
        
    state = fields.String(required=True)
    local_gov = fields.String(required=True)
    plot_size = fields.Float(required=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)
    
    predicted_yield = fields.Float(required=True)
    actual_yield = fields.Float(required=False)
    
    # Context fields
    region = fields.String(required=False)
    agro_zone = fields.String(required=False)
    soil_type = fields.String(required=False)
    pest_type = fields.String(required=False)
    pest_severity = fields.String(required=False)
    rainfall_variability = fields.String(required=False)
    labor_input = fields.String(required=False)

class YieldPredictionInputSchema(PredictionInputSchema):
    """
    Schema for validating yield prediction input data.
    Extends PredictionInputSchema to include crop_type and other specifics.
    """
    
    crop_type = fields.String(
        required=True,
        error_messages={"required": "Crop type is required for yield prediction"}
    )
    
    crop_variety = fields.String(load_default="Unknown")
    soil_type = fields.String(load_default="Unknown")
    pest_type = fields.String(load_default="None")
    pest_severity = fields.String(load_default="Low")
    region = fields.String(load_default="Unknown")
    state = fields.String(load_default="Unknown")
    agro_zone = fields.String(load_default="Unknown")
    farm_size_ha = fields.Float(load_default=1.0)
    labor_input = fields.String(load_default="Medium")
    rainfall_variability = fields.String(load_default="Medium")

    @validates('crop_type')
    def validate_crop_type(self, value: str, **kwargs) -> None:
        if not value or not value.strip():
            raise ValidationError("Crop type cannot be empty")


class YieldPredictionOutputSchema(Schema):
    """
    Schema for validating yield prediction output data.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    predicted_yield = fields.Float(
        required=True,
        error_messages={"required": "Predicted yield is required in response"}
    )
    
    unit = fields.String(
        required=True,
        validate=lambda x: x in ["kg/ha", "tons/ha"]
    )
    
    confidence_interval = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        dump_default=None
    )
    
    input_summary = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        required=False
    )


class BatchPredictionInputSchema(Schema):
    """
    Schema for validating batch prediction requests.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    samples = fields.List(
        fields.Nested(PredictionInputSchema),
        required=True,
        error_messages={
            "required": "Samples array is required for batch prediction",
            "invalid": "Samples must be an array of valid prediction inputs"
        }
    )
    
    @validates('samples')
    def validate_samples(self, value: list, **kwargs) -> None:
        """Validate samples list constraints."""
        if not value:
            raise ValidationError("Samples array cannot be empty")
        if len(value) > 100:
            raise ValidationError("Maximum 100 samples allowed per batch request")


class CropRequirementsSchema(Schema):
    """
    Schema for crop requirements output.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    crop = fields.String(required=True)
    requirements = fields.Dict(
        keys=fields.String(),
        values=fields.List(fields.Float()),
        required=True
    )


class ErrorResponseSchema(Schema):
    """
    Schema for error responses.
    Ensures consistent error format across the API.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    status = fields.String(
        required=True,
        validate=lambda x: x == "error"
    )
    
    message = fields.String(required=True)
    
    errors = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        required=False
    )
    
    timestamp = fields.String(required=True)


class SuccessResponseSchema(Schema):
    """
    Schema for successful responses.
    Ensures consistent success format across the API.
    """
    
    class Meta:
        unknown = EXCLUDE
    
    status = fields.String(
        required=True,
        validate=lambda x: x == "success"
    )
    
    timestamp = fields.String(required=True)
    
    data = fields.Raw(required=True)


# Convenience function for quick validation
def validate_prediction_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate prediction input data and return cleaned data.
    
    Args:
        data: Raw input dictionary
    
    Returns:
        Validated and cleaned data dictionary
    
    Raises:
        ValidationError: If validation fails
    """
    schema = PredictionInputSchema()
    return schema.load(data)


def validate_prediction_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate prediction output data and return serialized data.
    
    Args:
        data: Raw output dictionary
    
    Returns:
        Validated and serialized data dictionary
    
    Raises:
        ValidationError: If validation fails
    """
    schema = PredictionOutputSchema()
    return schema.dump(data)

class PredictionHistoryDumpSchema(Schema):
    """
    Schema for serializing a complete PredictionHistory database record.
    """
    id = fields.Integer()
    nitrogen = fields.Float()
    phosphorus = fields.Float()
    potassium = fields.Float()
    ph = fields.Float()
    humidity = fields.Float(allow_none=True)
    temperature = fields.Float(allow_none=True)
    rainfall = fields.Float(allow_none=True)
    
    recommended_crop = fields.String()
    confidence = fields.Float()
    
    state = fields.String(allow_none=True)
    local_gov = fields.String(allow_none=True)
    plot_size = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    latitude = fields.Float(allow_none=True)
    
    predicted_yield = fields.Float(allow_none=True)
    actual_yield = fields.Float(allow_none=True)
    yield_unit = fields.String(allow_none=True)
    
    timestamp = fields.DateTime(format="iso")