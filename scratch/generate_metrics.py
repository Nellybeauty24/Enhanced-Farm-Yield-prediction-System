import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import os

# Create outputs dir if it doesn't exist
os.makedirs('outputs', exist_ok=True)

print("Loading data...")
df = pd.read_csv('data/nigeria_agri_yield_cleaned.csv')

# Feature engineering
df['soil_fertility_index'] = df['soil_nitrogen'] + df['soil_phosphorus'] + df['soil_potassium']
df['np_ratio'] = df['soil_nitrogen'] / (df['soil_phosphorus'] + 1e-6)
df['climate_index'] = df['rainfall_mm'] * df['temperature_C']
df['ph_stress'] = (df['soil_pH'] - 7.0).abs()

cat_cols = ['region', 'state', 'agro_zone', 'soil_type', 'pest_type', 'pest_severity', 'rainfall_variability', 'labor_input']
num_cols = ['soil_nitrogen', 'soil_phosphorus', 'soil_potassium', 'soil_pH', 'temperature_C', 'rainfall_mm', 'farm_size_ha', 'soil_fertility_index', 'np_ratio', 'climate_index', 'ph_stress']
target = 'crop_type'

df_clean = df[cat_cols + num_cols + [target]].dropna()
X = df_clean[cat_cols + num_cols]
y = df_clean[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Loading model...")
model = CatBoostClassifier()
model.load_model('models/crop_model.cbm')

print("Generating predictions...")
y_pred = model.predict(X_test)

# 1. Classification Report
print("\n--- CLASSIFICATION REPORT ---")
report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()
print(report_df.to_csv())

# 2. Confusion Matrix
print("\n--- GENERATING CONFUSION MATRIX ---")
cm = confusion_matrix(y_test, y_pred)
classes = model.classes_

fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)

ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=classes, yticklabels=classes,
       title='Crop Prediction Confusion Matrix',
       ylabel='True Label',
       xlabel='Predicted Label')

plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
fmt = 'd'
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], fmt),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")

fig.tight_layout()
plt.savefig('outputs/confusion_matrix.png')
print("Confusion matrix saved to outputs/confusion_matrix.png")
