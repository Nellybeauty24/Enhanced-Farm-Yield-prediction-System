"""
Schemas package initialization.
Exports validation schemas for API request/response validation.
"""

from .prediction_schema import (
    PredictionInputSchema,
    PredictionOutputSchema,
    BatchPredictionInputSchema
)

__all__ = [
    'PredictionInputSchema',
    'PredictionOutputSchema',
    'BatchPredictionInputSchema'
]