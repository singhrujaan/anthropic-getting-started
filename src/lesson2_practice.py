import json
from typing import Optional

from pydantic import BaseModel, ValidationError, field_validator


class WeatherReading(BaseModel):
    city: str
    temperature_celsius: float
    humidity_percent: float
    conditions: str
    wind_speed_kmh: float = 0.0
    feels_like_celsius: Optional[float] = None

    @field_validator("humidity_percent")
    @classmethod
    def validate_humidity(cls, v) -> float:
        if not 0 <= v <= 100:
            raise ValueError("Humidity must be between 0 and 100")
        return round(v, 4)

    @field_validator("city")
    @classmethod
    def validate_city(cls, v) -> str:
        return v.strip().title()


def parse_json(raw_json: str) -> Optional[WeatherReading]:
    try:
        data = json.loads(raw_json)
        result = WeatherReading(**data)
        return result
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None


# --- Test all paths, not just the happy path ---

good_response = """
{
    "city": "denver colorado",
    "temperature_celsius": 17,
    "humidity_percent": 70,
    "conditions": "good",
    "wind_speed_kmh": 55
}
"""

bad_humidity = """
{
    "city": "Denver",
    "temperature_celsius": 20,
    "humidity_percent": 150,
    "conditions": "cloudy"
}
"""

bad_json = '{"city": "Denver", broken json'

print("--- Good response ---")
r = parse_json(good_response)
if r:
    print(f"City: {r.city}")  # "Denver Colorado" — title case
    print(f"Temp: {r.temperature_celsius}")
    print(f"Wind default: {r.wind_speed_kmh}")
    print(f"Feels like: {r.feels_like_celsius}")  # None

print("\n--- Bad humidity ---")
r = parse_json(bad_humidity)
print(f"Result: {r}")  # None

print("\n--- Broken JSON ---")
r = parse_json(bad_json)
print(f"Result: {r}")  # None
