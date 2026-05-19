from catboost import CatBoostClassifier, CatBoostRegressor
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else '.'

crop_model_path = os.path.join(base_dir, 'models', 'crop_model.cbm')
yield_model_path = os.path.join(base_dir, 'models', 'catboost_model.cbm')

print("--- DIAGNOSTIC MODEL CHECK ---")
if os.path.exists(crop_model_path):
    clf = CatBoostClassifier()
    clf.load_model(crop_model_path)
    print("Classifier Model Loaded Successfully.")
    print("Classifier Features:", clf.feature_names_)
else:
    print("Classifier Model NOT FOUND at", crop_model_path)

if os.path.exists(yield_model_path):
    reg = CatBoostRegressor()
    reg.load_model(yield_model_path)
    print("Regressor Model Loaded Successfully.")
    print("Regressor Features:", reg.feature_names_)
else:
    print("Regressor Model NOT FOUND at", yield_model_path)
