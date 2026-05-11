# Analytics API Documentation

This document provides a detailed explanation of the functions within `app/api/analytics.py`. It explains how the system processes historical data to provide insights for the user dashboard.

## Overview
The Analytics API is the "history teacher" of the system. It looks at all the predictions and harvest logs a farmer has saved in the past and summarizes them into charts and statistics. This helps farmers answer questions like "How is my farm doing compared to last year?" or "Which crop is making me the most money?"

---

## 1. Summary Statistics (`/summary`)

### 👨‍🌾 Layman's Explanation
Think of this as the "Dashboard Snapshot." It gives you the big numbers at a glance: how many times you've used the app, your average harvest weight, and which crop you plant most often. It also calculates the "Yield Gap"—which is the difference between what the AI predicted and what you actually harvested.

### ⚙️ Technical Logic
1. **Filtering**: Checks if you want stats for *all* crops or just a *specific* one (using the `crop` filter).
2. **Aggregation**: Uses database functions (`func.avg`, `func.count`) to calculate:
   - Total number of records.
   - Average AI confidence.
   - Average predicted vs. average actual yield.
3. **Yield Gap Calculation**: Subtracts the predicted average from the actual average.
4. **Recent Activity**: Counts how many predictions were made in the last 24 hours.

### 📥 Request Parameters (Query Strings)
- `crop` (Optional): Filter results for a specific crop name (e.g., `?crop=maize`).

### 📤 Response Object
```json
{
  "status": "success",
  "data": {
    "total_predictions": 15,
    "avg_confidence": 0.8921,
    "top_crop": "maize",
    "avg_yield": 2100.50,
    "avg_actual": 2350.00,
    "yield_diff": 249.50,
    "recent_activity": 2
  },
  "timestamp": "2026-04-05T04:48:00Z"
}
```

---

## 2. Yield History Trend (`/yield-history`)

### 👨‍🌾 Layman's Explanation
This is the "Timeline" view. It shows how your harvest yields have changed month-by-month over the last year. It helps you see seasonal patterns—for example, if your harvest is always lower in June compared to December.

### ⚙️ Technical Logic
1. **Time Window**: Defaults to looking back 365 days, but can be customized.
2. **Grouping**: Groups database records by month (e.g., "2024-01", "2024-02").
3. **Processing**: Calculates the average yield for each of those months.
4. **Formatting**: Converts technical dates (like `2024-01`) into friendly names (like `Jan`).

### 📥 Request Parameters
- `days` (Optional): Number of days to look back. Defaults to `365`.

### 📤 Response Object
```json
{
  "status": "success",
  "data": {
    "history": [
      { "month": "Jan", "yield": 2000.0, "count": 2 },
      { "month": "Feb", "yield": 2150.0, "count": 1 }
    ],
    "period_days": 365
  }
}
```

---

## 3. Crop Comparison (`/crop-comparison`)

### 👨‍🌾 Layman's Explanation
This is the "Versus" mode. It compares different crops against each other based on your data. For example, it shows you that while you plant "Rice" more often, "Maize" actually gives you a higher weight of food per hectare.

### ⚙️ Technical Logic
1. **Grouping**: Groups all your saved records by there `recommended_crop` type.
2. **Comparison**: For each crop type, it calculates:
   - How many times it was recommended (`count`).
   - The average AI confidence for those recommendations.
   - The average yield achieved.
3. **Sorting**: Orders the list from the highest-yielding crop to the lowest.

### 📥 Request Parameters
*None (Returns all crops saved by the user).*

### 📤 Response Object
```json
{
  "status": "success",
  "data": {
    "distribution": [
      { "crop": "maize", "yield": 2500.0, "count": 5, "avg_confidence": 0.92 },
      { "crop": "rice", "yield": 1800.0, "count": 8, "avg_confidence": 0.88 }
    ]
  }
}
```

---

## 4. History Records (`/history-records`)

### 👨‍🌾 Layman's Explanation
This is the "Digital Logbook." It is a complete, detailed list of every single prediction scan you have ever saved. It includes everything: the soil nutrients (NPK), the weather at the time, where the farm is located, and the final result.

### ⚙️ Technical Logic
1. **Query**: Pulls every record from the `PredictionHistory` table belonging to the user.
2. **Sorting**: Shows the newest scans first (`timestamp desc`).
3. **Serialization**: Uses a "Dump Schema" to convert the database rows into a clean JSON format that includes all geographic and soil details.

### 📥 Request Parameters
*None.*

### 📤 Response Object
```json
{
  "status": "success",
  "data": [
    {
      "id": 101,
      "timestamp": "2026-03-01T10:00:00",
      "recommended_crop": "maize",
      "nitrogen": 85.0,
      "phosphorus": 40.0,
      "potassium": 40.0,
      "ph": 6.2,
      "state": "Kano",
      "predicted_yield": 2400.0,
      "actual_yield": 2450.0
    },
    ...
  ]
}
```

---

## Summary of Analytics Endpoints

| Feature | Method | Key Purpose | Dashboard Component |
| :--- | :--- | :--- | :--- |
| **Summary** | `GET` | Overall stats (Totals, Averages) | Header Cards (Top Stats) |
| **History** | `GET` | Performance over time | Growth/Trend Line Chart |
| **Comparison** | `GET` | Best vs. Worst crops | Bar Chart (Crop Comparison) |
| **Records** | `GET` | Raw log data | Detailed Data Table |

---
*Generated by Antigravity AI*
