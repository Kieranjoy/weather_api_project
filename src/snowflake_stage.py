import os
import snowflake.connector as sc
from dotenv import load_dotenv
from snowflake.core import Root
from snowflake.core.stage import Stage, StageEncryption, StageCollection
from main import parquet_list
from snowflake.connector.errors import DatabaseError, ProgrammingError
load_dotenv()

#obtain confidential credentials from .env to authenticate
private_key_file = 'snowflake_private_key.p8'
private_key_file_pwd = os.getenv('password')
user = os.getenv('user')
account = os.getenv('account')
authenticator = os.getenv('authenticator')
warehouse = os.getenv('warehouse')
database = os.getenv('database')
schema = os.getenv('schema')

#create parameters to connect to snowflake
conn_params = {
    'account': account,
    'user': user,
    'authenticator': authenticator,
    'private_key_file': private_key_file,
    'private_key_file_pwd':private_key_file_pwd,
    'warehouse': warehouse,
    'database': database,
    'schema': schema
}

#connect to snowflake using defined parameters
ctx = sc.connect(**conn_params)
cs = ctx.cursor()

root = Root(ctx)

# Check connection works and pulls stages through
# stages: StageCollection = root.databases["TIL_DATA_ENGINEERING"].schemas["JC_NATURE"].stages
# stage_iter = stages.iter(like="NATURE_STG")  # returns a PagedIter[Stage]
# for stage_obj in stage_iter:
#   print(stage_obj.name)

stages: StageCollection = root.databases[f"{database}"].schemas[f"{schema}"].stages

stage_list = list(stages.iter(like="WEATHER_STG"))
print(f"{stage_list}")
if stage_list:
  my_stage_res = root.databases[f"{database}"].schemas[f"{schema}"].stages["WEATHER_STG"]
  for element in parquet_list:
      my_stage_res.put(f"./staging/{element}", "/")  
else:
#create stage in snowflake to store parquets in
  new_stage = Stage(
    name="WEATHER_STG",
    encryption=StageEncryption(type="SNOWFLAKE_SSE")
  )
  root.databases[f"{database}"].schemas[f"{schema}"].stages.create(new_stage)
  my_stage_res = root.databases[f"{database}"].schemas[f"{schema}"].stages["WEATHER_STG"]
  for element in parquet_list:
    my_stage_res.put(f"./staging/{element}", "/")



# Create the current forecast table and copy the parquet into it in snowflake

cs.execute(f"USE WAREHOUSE {warehouse};")
cs.execute(f"USE DATABASE {database};")
cs.execute(f"USE SCHEMA {schema};")

cs.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
print(cs.fetchone())

try:
  cs.execute("CREATE OR REPLACE TABLE " \
                      "c_forecast_table( " \
                      "date VARIANT, " \
                      "load_date VARIANT, " \
                      "sunrise VARIANT, " \
                      "sunset VARIANT, " \
                      "temperature_2m_mean VARIANT, " \
                      "cloud_cover_mean VARIANT," \
                      "leaf_wetness_probability_mean VARIANT, " \
                      "precipitation_probability_mean VARIANT, " \
                      "relative_humidity_2m_mean VARIANT, " \
                      "visibility_mean VARIANT, " \
                      "wind_speed_10m_mean VARIANT, " \
                      "wind_gusts_10m_mean VARIANT, " \
                      "wind_direction_10m_dominant VARIANT, " \
                      "uv_index_max VARIANT, " \
                      "daylight_duration VARIANT, " \
                      "sunshine_duration VARIANT, " \
                      "rain_sum VARIANT, " \
                      "showers_sum VARIANT, " \
                      "snowfall_sum VARIANT, " \
                      "precipitation_sum VARIANT, " \
                      "precipitation_hours VARIANT); ")

  cs.execute("GRANT SELECT ON TABLE c_forecast_table TO ROLE DATASCHOOL;")

except ProgrammingError as e:
    print(f"Snowflake ProgrammingError: {e}")
    print(f"Error code: {e.errno}")
    print(f"SQL state: {e.sqlstate}")
    print(f"Message: {e.msg}")
except DatabaseError as e:
  print(f"error: {e}")

try:
  cs.execute("COPY INTO c_forecast_table " \
                      "FROM @WEATHER_STG " \
                        "FILES = ('current_forecast.parquet') " \
                          "FILE_FORMAT = (TYPE = PARQUET) " \
                            "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;")
  print("successful run 1")
except ProgrammingError as e:
    print(f"Snowflake ProgrammingError: {e}")
    print(f"Error code: {e.errno}")
    print(f"SQL state: {e.sqlstate}")
    print(f"Message: {e.msg}")
except DatabaseError as e:
  print(f"error: {e}")  

# Create the historic forecast table and copy the parquet into it in snowflake

cs.execute(f"USE WAREHOUSE {warehouse}")
cs.execute(f"USE DATABASE {database}")
cs.execute(f"USE SCHEMA {schema}")

try:
  cs.execute("CREATE OR REPLACE TABLE " \
                    "h_forecast_table( " \
                    "date VARIANT, " \
                    "load_date VARIANT, "
                      "sunrise VARIANT, " \
                      "sunset VARIANT, " \
                      "soil_moisture_0_to_7cm_mean VARIANT, " \
                      "temperature_2m_mean VARIANT, " \
                      "cloud_cover_mean VARIANT, " \
                      "leaf_wetness_probability_mean VARIANT, " \
                      "precipitation_probability_mean VARIANT, " \
                      "relative_humidity_2m_mean VARIANT, " \
                      "visibility_mean VARIANT, " \
                      "winddirection_10m_dominant VARIANT, " \
                      "wind_gusts_10m_mean VARIANT, " \
                      "wind_speed_10m_mean VARIANT, " \
                      "soil_temperature_0_to_7cm_mean VARIANT, " \
                      "uv_index_max VARIANT, " \
                      "daylight_duration VARIANT, " \
                      "sunshine_duration VARIANT, " \
                      "rain_sum VARIANT, " \
                      "showers_sum VARIANT, " \
                      "snowfall_sum VARIANT, " \
                      "precipitation_sum VARIANT, " \
                      "precipitation_hours VARIANT);")
  
  cs.execute("GRANT SELECT ON TABLE h_forecast_table TO ROLE DATASCHOOL;")

  cs.execute("COPY INTO h_forecast_table " \
                    "FROM @WEATHER_STG " \
                    "FILES = ('historic_forecast.parquet') " \
                    "FILE_FORMAT = (TYPE = PARQUET) " \
                    "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;")

except ProgrammingError as e:
    print(f"Snowflake ProgrammingError: {e}")
    print(f"Error code: {e.errno}")
    print(f"SQL state: {e.sqlstate}")
    print(f"Message: {e.msg}")
except DatabaseError as e:
  print(f"error: {e}")  
print("successful run 2")

# Create the historic weather table and copy the parquet into it in snowflake

cs.execute(f"USE WAREHOUSE {warehouse}")
cs.execute(f"USE DATABASE {database}")
cs.execute(f"USE SCHEMA {schema}")

try:
  cs.execute("CREATE OR REPLACE TABLE " \
                    "h_weather_table( " \
                    "date VARIANT, " \
                    "load_date VARIANT, "
                      "sunrise VARIANT, " \
                      "sunset VARIANT, " \
                      "soil_moisture_0_to_7cm_mean VARIANT, " \
                      "temperature_2m_mean VARIANT, " \
                      "cloud_cover_mean VARIANT, " \
                      "leaf_wetness_probability_mean VARIANT, " \
                      "precipitation_probability_mean VARIANT, " \
                      "relative_humidity_2m_mean VARIANT, " \
                      "visibility_mean VARIANT, " \
                      "winddirection_10m_dominant VARIANT, " \
                      "wind_gusts_10m_mean VARIANT, " \
                      "wind_speed_10m_mean VARIANT, " \
                      "soil_temperature_0_to_7cm_mean VARIANT, " \
                      "uv_index_max VARIANT, " \
                      "daylight_duration VARIANT, " \
                      "sunshine_duration VARIANT, " \
                      "rain_sum VARIANT, " \
                      "showers_sum VARIANT, " \
                      "snowfall_sum VARIANT, " \
                      "precipitation_sum VARIANT, " \
                      "precipitation_hours VARIANT);")
  
  cs.execute("GRANT SELECT ON TABLE h_weather_table TO ROLE DATASCHOOL;")

  cs.execute("COPY INTO h_weather_table " \
                    "FROM @WEATHER_STG " \
                    "FILES = ('historic_weather.parquet') " \
                    "FILE_FORMAT = (TYPE = PARQUET) " \
                    "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;")

except ProgrammingError as e:
    print(f"Snowflake ProgrammingError: {e}")
    print(f"Error code: {e.errno}")
    print(f"SQL state: {e.sqlstate}")
    print(f"Message: {e.msg}")
except DatabaseError as e:
  print(f"error: {e}")  
print("successful run 3")

# Create the special forecast table and copy into it
cs.execute(f"USE WAREHOUSE {warehouse}")
cs.execute(f"USE DATABASE {database}")
cs.execute(f"USE SCHEMA {schema}")

try:
  cs.execute("CREATE OR REPLACE TABLE " \
                    "special_table( " \
                    "date VARIANT, " \
                    "load_date VARIANT, " \
                    "soil_temperature_6cm VARIANT, " \
                    "soil_moisture_3_to_9cm VARIANT, " \
                    "soil_temperature_0cm VARIANT, " \
                    "soil_moisture_0_to_1cm VARIANT, " \
                    "soil_moisture_1_to_3cm VARIANT);") \
                    
  cs.execute("GRANT SELECT ON TABLE special_table TO ROLE DATASCHOOL;")

  cs.execute("COPY INTO special_table " \
                    "FROM @WEATHER_STG " \
                    "FILES = ('special_forecast.parquet') " \
                    "FILE_FORMAT = (TYPE = PARQUET) " \
                    "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;")


except ProgrammingError as e:
    print(f"Snowflake ProgrammingError: {e}")
    print(f"Error code: {e.errno}")
    print(f"SQL state: {e.sqlstate}")
    print(f"Message: {e.msg}")
except DatabaseError as e:
  print(f"error: {e}")  
print("successful run 4")



