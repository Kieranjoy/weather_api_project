import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
	"latitude": 51.9411,
	"longitude": -1.5453,
	"hourly": ["soil_temperature_6cm", "soil_moisture_3_to_9cm", "soil_temperature_0cm", "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm"],
	"timezone": "GMT",
	"forecast_days": 15,
	"wind_speed_unit": "mph",
}
def extract_special():
    params = PARAMS.copy()
    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Print details to check response is working
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_soil_temperature_6cm = hourly.Variables(0).ValuesAsNumpy()
    hourly_soil_moisture_3_to_9cm = hourly.Variables(1).ValuesAsNumpy()
    hourly_soil_temperature_0cm = hourly.Variables(2).ValuesAsNumpy()
    hourly_soil_moisture_0_to_1cm = hourly.Variables(3).ValuesAsNumpy()
    hourly_soil_moisture_1_to_3cm = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )
    }

    hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
    hourly_data["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
    hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
    hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
    hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm

    special_df = pd.DataFrame(data = hourly_data)
    special_df["load_date"] = pd.Timestamp.now()
   

    return special_df