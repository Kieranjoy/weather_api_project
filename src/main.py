from historical_forecast import extract_hforecast
from historical_weather import extract_hweather
from forecast_weather import extract_cforecast
from special_forecast import extract_special

from datetime import datetime
from pathlib import Path

today = datetime.now().strftime("%Y-%m-%d")

staging = Path("staging") 
staging.mkdir(exist_ok=True)


hforecast_data = extract_hforecast()
hweather_data = extract_hweather()
cforecast_data = extract_cforecast()
special_data = extract_special()

# Check function calls are being called correctly
# print("\nHistorical Forecast\n", hforecast_data)
# print("\nHistorical Weather\n", hweather_data)
# print("\nCurrent Forecast\n", cforecast_data)
print("\nSpecial Forecast\n", special_data)

hforecast_data.to_parquet(staging / "historic_forecast.parquet",index=False)
hweather_data.to_parquet(staging / "historic_weather.parquet",index=False)
cforecast_data.to_parquet(staging / "current_forecast.parquet",index=False)
special_data.to_parquet(staging / "special_forecast.parquet", index=False)

parquet_list = ["historic_forecast.parquet","historic_weather.parquet","current_forecast.parquet","special_forecast.parquet"]


