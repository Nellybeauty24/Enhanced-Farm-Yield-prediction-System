import requests

data = {
    "nitrogen": 30,
    "phosphorus": 30,
    "potassium": 49,
    "ph": 4.7,
    "temperature": 44.6,
    "rainfall": 499.7
}

try:
    response = requests.post("http://localhost:5000/api/v1/predict", json=data)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print(f"Request failed: {e}")
