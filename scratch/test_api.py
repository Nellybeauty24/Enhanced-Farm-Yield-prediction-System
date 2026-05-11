import requests

url = "http://localhost:5000/api/v1/predict"
payload = {
    "nitrogen": 10,
    "phosphorus": 10,
    "potassium": 10,
    "ph": 7,
    "temperature": 25,
    "rainfall": 100
}
try:
    response = requests.post(url, json=payload)
    print(response.json())
except Exception as e:
    print("Error:", e)
