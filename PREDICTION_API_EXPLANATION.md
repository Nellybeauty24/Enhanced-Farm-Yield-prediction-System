# Prediction API Documentation

This document provides a detailed explanation of the functions within `app/api/prediction.py`. It is designed to be understood by both developers and non-technical stakeholders (laymen).

## Overview
The Prediction API is the "brain" of the Soil Nutrition system. its primary job is to take soil data (like Nitrogen, Phosphorus, Potassium, and pH levels) and environmental data (like Temperature and Rainfall) and tell the farmer two things:
1. **What crop should I plant?** (Crop Prediction)
2. **How much harvest can I expect?** (Yield Prediction)

---

## 1. Crop Prediction (`/predict`)

### 👨‍🌾 Layman's Explanation
Imagine you have a handful of soil and you want to know what will grow best in it. You give the system your soil test results (Nitrogen, Phosphorus, etc.) and the local weather info. The system looks at its "knowledge base" and says: "I am 95% sure you should plant Rice, and here are some tips on how to manage it."

### ⚙️ Technical Logic
1. **Authentication**: Checks if the user is logged in (`@require_auth`).
2. **Input Validation**: Uses `PredictionInputSchema` to ensure all numbers are valid and within realistic ranges (e.g., pH between 0 and 14).
3. **ML Prediction**: Calls `CropPredictionService.predict()` which uses a pre-trained Machine Learning model to calculate the most suitable crop and a confidence score.
4. **Recommendation Generation**: Calls `RecommendationService.generate_recommendations()` to provide specific farming advice based on the predicted crop and soil levels.
5. **Response**: Returns the recommended crop, the probability (how sure the AI is), and the advice.

### 📥 Request Object (What you send)
```json
{
  "nitrogen": 90.0,
  "phosphorus": 42.0,
  "potassium": 43.0,
  "ph": 6.5,
  "temperature": 20.8,
  "humidity": 82.0,
  "rainfall": 202.9
}
```

### 📤 Response Object (What you get back)
```json
{
  "status": "success",
  "data": {
    "recommended_crop": "rice",
    "probability": 0.9452,
    "recommendations": [
      "Ensure consistent flooding during early growth stages.",
      "Monitor for stem borer pests."
    ],
    "input_summary": {
      "nitrogen": 90.0,
      "phosphorus": 42.0,
      "potassium": 43.0,
      "ph": 6.5
    }
  },
  "timestamp": "2026-04-05T04:00:00Z"
}
```

---

## 2. Yield Prediction (`/predict-yield`)

### 👨‍🌾 Layman's Explanation
Once you know *what* to plant, you want to know *how much* you'll actually harvest. You tell the system the crop type and your soil/weather data, and it estimates your final harvest weight (in kg per hectare).

### ⚙️ Technical Logic
1. **Validation**: Uses `YieldPredictionInputSchema`. This is stricter because it needs to know the specific `crop_type` you are asking about.
2. **Calculation**: Uses `crop_service.predict_yield()` to run a separate ML model specifically for weight estimation.
3. **Response**: Returns the estimated yield in `kg/ha`.

### 📥 Request Object
```json
{
  "nitrogen": 90.0,
  "phosphorus": 42.0,
  "potassium": 43.0,
  "ph": 6.5,
  "temperature": 20.0,
  "rainfall": 200.0,
  "crop_type": "maize"
}
```

### 📤 Response Object
```json
{
  "status": "success",
  "data": {
    "predicted_yield": 2450.5,
    "unit": "kg/ha",
    "input_summary": { ... }
  }
}
```

---

## 3. Save Prediction (`/predict/save`)

### 👨‍🌾 Layman's Explanation
This is like "bookmarking" or "saving" a report. It takes the prediction results and saves them into the system's permanent memory so the farmer can look back at them later or compare them with their actual harvest.

### ⚙️ Technical Logic
1. **Validation**: Uses `PredictionSaveSchema`. This requires more detail, including geographic location (`latitude`, `longitude`) and `plot_size`.
2. **Database Storage**: Creates a new record in the `PredictionHistory` table in the database.
3. **Association**: Ties the record to the currently logged-in user.

### 📥 Request Object
```json
{
  "nitrogen": 80,
  "phosphorus": 40,
  "potassium": 40,
  "ph": 6.5,
  "recommended_crop": "Maize",
  "confidence": 0.88,
  "state": "Kano",
  "local_gov": "Ungogo",
  "plot_size": 2.5,
  "longitude": 8.52,
  "latitude": 12.01,
  "predicted_yield": 1200.5
}
```

---

## 4. Update Actual Yield (`/predict/<id>/actual-yield`)

### 👨‍🌾 Layman's Explanation
After the harvest is done, the farmer can come back and enter the *real* amount of food they gathered. This helps the system learn and show the farmer the "Performance Gap" (the difference between what the AI predicted and what actually happened).

### ⚙️ Technical Logic
1. **Lookup**: Finds the saved prediction by its ID.
2. **Ownership Check**: Ensures the user trying to update the record is the one who created it.
3. **Update**: Changes the `actual_yield` field in the database.

### 📥 Request Object
```json
{
  "actual_yield": 2300.0
}
```

---

## 5. Metadata Endpoints

### 📜 List Available Crops (`/crops`)
*   **What it does**: Simply lists all the different types of crops the system knows about (e.g., Rice, Maize, Beans).
*   **Use case**: Helps a developer build a dropdown menu in a mobile app.

### 📏 Get Crop Requirements (`/crops/<crop_name>/requirements`)
*   **What it does**: Returns the "ideal" conditions for a specific crop based on top-performing historical harvests.
*   **Use case**: A farmer wants to know "What is the perfect pH for Rice?" without running a full prediction.

---

## Summary of Request/Response Patterns

| Feature | Method | Auth Required? | Primary Input | Primary Output |
| :--- | :--- | :--- | :--- | :--- |
| **Predict Crop** | `POST` | Yes | Soil + Weather data | Crop Name + Probability |
| **Predict Yield** | `POST` | No | Soil + Weather + Crop | Expected kg/ha |
| **Save Result** | `POST` | Yes | Full Data + Location | Success Message |
| **Log Harvest** | `PATCH` | Yes | Actual Yield amount | Success Message |
| **List Crops** | `GET` | No | None | List of crop names |

---
*Generated by Antigravity AI*
