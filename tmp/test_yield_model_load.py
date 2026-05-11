import sys
sys.path.append('.')
from app.services.crop_service import CropPredictionService

print("Testing model load...")
try:
    service = CropPredictionService()
    # It attempts to load during init...
    if service._yield_model_loaded:
        print("Yield model loaded successfully!")
    else:
        print("Yield model failed to load. Manually testing load_yield_model")
        try:
            service._load_yield_model()
            if service._yield_model_loaded:
                print("Loaded on second try")
        except Exception as e:
            import traceback
            traceback.print_exc()

except Exception as e:
    import traceback
    traceback.print_exc()
