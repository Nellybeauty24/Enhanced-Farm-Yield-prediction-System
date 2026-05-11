class ModelNotLoadedError(Exception):
    """Raised when the model is not loaded."""
    pass

class PredictionError(Exception):
    """Raised when prediction fails."""
    pass

class InvalidInputError(Exception):
    """Raised when input data is invalid."""
    pass
