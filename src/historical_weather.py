import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
yesterday = datetime.today().date() - timedelta(days=1)
url = "https://archive-api.open-meteo.com/v1/archive"
PARAMS = {
"latitude": 51.9411,
	"longitude": -1.5453,
	"start_date": "1940-01-01",
	"end_date": f"{yesterday}",
	"daily": ["sunrise", "sunset", "soil_moisture_0_to_7cm_mean", "temperature_2m_mean", "cloud_cover_mean", "leaf_wetness_probability_mean", "precipitation_probability_mean", "relative_humidity_2m_mean", "visibility_mean", "winddirection_10m_dominant", "wind_gusts_10m_mean", "wind_speed_10m_mean", "soil_temperature_0_to_7cm_mean", "uv_index_max", "daylight_duration", "sunshine_duration", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours"],
	"timezone": "GMT",
	"wind_speed_unit": "mph",
}
def extract_hweather():
	params = PARAMS.copy()
	responses = openmeteo.weather_api(url, params = params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	# print(f"Elevation: {response.Elevation()} m asl")
	# print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
	# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
	daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()
	daily_soil_moisture_0_to_7cm_mean = daily.Variables(2).ValuesAsNumpy()
	daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
	daily_cloud_cover_mean = daily.Variables(4).ValuesAsNumpy()
	daily_leaf_wetness_probability_mean = daily.Variables(5).ValuesAsNumpy()
	daily_precipitation_probability_mean = daily.Variables(6).ValuesAsNumpy()
	daily_relative_humidity_2m_mean = daily.Variables(7).ValuesAsNumpy()
	daily_visibility_mean = daily.Variables(8).ValuesAsNumpy()
	daily_winddirection_10m_dominant = daily.Variables(9).ValuesAsNumpy()
	daily_wind_gusts_10m_mean = daily.Variables(10).ValuesAsNumpy()
	daily_wind_speed_10m_mean = daily.Variables(11).ValuesAsNumpy()
	daily_soil_temperature_0_to_7cm_mean = daily.Variables(12).ValuesAsNumpy()
	daily_uv_index_max = daily.Variables(13).ValuesAsNumpy()
	daily_daylight_duration = daily.Variables(14).ValuesAsNumpy()
	daily_sunshine_duration = daily.Variables(15).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(16).ValuesAsNumpy()
	daily_showers_sum = daily.Variables(17).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(18).ValuesAsNumpy()
	daily_precipitation_sum = daily.Variables(19).ValuesAsNumpy()
	daily_precipitation_hours = daily.Variables(20).ValuesAsNumpy()

	daily_data = {
		"date": pd.date_range(
			start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = daily.Interval()),
			inclusive = "left"
		)
	}

	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["soil_moisture_0_to_7cm_mean"] = daily_soil_moisture_0_to_7cm_mean
	daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
	daily_data["cloud_cover_mean"] = daily_cloud_cover_mean
	daily_data["leaf_wetness_probability_mean"] = daily_leaf_wetness_probability_mean
	daily_data["precipitation_probability_mean"] = daily_precipitation_probability_mean
	daily_data["relative_humidity_2m_mean"] = daily_relative_humidity_2m_mean
	daily_data["visibility_mean"] = daily_visibility_mean
	daily_data["winddirection_10m_dominant"] = daily_winddirection_10m_dominant
	daily_data["wind_gusts_10m_mean"] = daily_wind_gusts_10m_mean
	daily_data["wind_speed_10m_mean"] = daily_wind_speed_10m_mean
	daily_data["soil_temperature_0_to_7cm_mean"] = daily_soil_temperature_0_to_7cm_mean
	daily_data["uv_index_max"] = daily_uv_index_max
	daily_data["daylight_duration"] = daily_daylight_duration
	daily_data["sunshine_duration"] = daily_sunshine_duration
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["showers_sum"] = daily_showers_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum
	daily_data["precipitation_sum"] = daily_precipitation_sum
	daily_data["precipitation_hours"] = daily_precipitation_hours

	hweather_df = pd.DataFrame(data = daily_data)
	hweather_df["load_date"] = pd.Timestamp.now()

	return hweather_df