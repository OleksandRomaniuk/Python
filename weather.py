import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = 
RSA_KEY = 
app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location: str, date: str):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    params = {
        "location": location,
        "startDateTime": date,
        "endDateTime": date,
        "unitGroup": "metric", 
        "key": RSA_KEY,
        "contentType": "json",
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage("Failed to fetch weather data", status_code=response.status_code)

def analyze_weather(weather_data):
    conditions = weather_data["days"][0].get("conditions", "")
    temp = weather_data["days"][0].get("temp")
    uv_index = weather_data["days"][0].get("uvindex", 0)
    wind_kph = weather_data["days"][0].get("windspeed", 0)
    pressure_mb = weather_data["days"][0].get("pressure", 0)
    humidity = weather_data["days"][0].get("humidity", 0)
    
    simplified_weather = {
        "temp": temp,
        "conditions": conditions,
        "uv_index": uv_index,
        "wind_kph": wind_kph,
        "pressure_mb": pressure_mb,
        "humidity": humidity
    }

    return simplified_weather

@app.route("/weather/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if not json_data or "token" not in json_data or json_data.get("token") != API_TOKEN:
        raise InvalidUsage("Invalid or missing API token", status_code=403)

    location = json_data.get("location")
    date = json_data.get("date")

    if not location or not date:
        raise InvalidUsage("Location and date are required", status_code=400)

    weather_data = get_weather(location, date)
    simplified_weather = analyze_weather(weather_data)

    end_dt = dt.datetime.now()

    result = {
        "requester_name": json_data.get("requester_name"),
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "location": location,
        "date": date,
        "weather": simplified_weather,
    }

    return jsonify(result)