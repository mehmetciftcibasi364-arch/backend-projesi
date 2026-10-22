import requests
from fastapi import FastAPI
from decision_engine import make_decision
from database import create_database, save_sensor_data, get_sensor_data
from sentinel_service import get_sentinel_data
app = FastAPI(
    title="Backend API",
    version="1.0.0"
)
create_database()
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Backend API calisiyor"
    }
@app.get("/api/weather")
def get_weather(latitude: float, longitude: float):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        weather = response.json()["current"]

        return {
            "status": "success",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "weather": {
                "temperature": weather["temperature_2m"],
                "humidity": weather["relative_humidity_2m"],
                "precipitation": weather["precipitation"],
                "wind_speed": weather["wind_speed_10m"],
                "time": weather["time"]
            }
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }
from pydantic import BaseModel


class SensorData(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    soil_moisture: float


@app.post("/api/sensors")
def receive_sensor_data(data: SensorData):

    save_sensor_data(
        data.device_id,
        data.temperature,
        data.humidity,
        data.soil_moisture
    )

    return {
        "status": "success",
        "message": "Sensor verisi veritabanina kaydedildi",
        "data": data
    }
@app.get("/api/sensors")
def read_sensor_data():
    data = get_sensor_data()

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }
@app.get("/api/decision")
def get_decision():
    sensor_records = get_sensor_data()

    if not sensor_records:
        return {
            "status": "error",
            "message": "Sensor verisi bulunamadi"
        }

    latest = sensor_records[0]

    decision = make_decision(
        latest["temperature"],
        latest["humidity"],
        latest["soil_moisture"]
    )

    return {
        "status": "success",
        "sensor_data": latest,
        "decision": decision
    }
@app.get("/api/sentinel")
def sentinel_data(latitude: float, longitude: float):
    return get_sentinel_data(latitude, longitude)