SELECT
    TO_DATE(TO_TIMESTAMP_NTZ(load_date::NUMBER / 1000000)) AS load_date,
    DATE::TIMESTAMP::DATE AS date,
    CAST(CONVERT_TIMEZONE('UTC','Europe/London',TO_TIMESTAMP_NTZ(sunrise::NUMBER)) AS TIME) AS sunrise_time,
    CAST(CONVERT_TIMEZONE('UTC','Europe/London',TO_TIMESTAMP_NTZ(sunset::NUMBER)) AS TIME) AS sunset_time,
    ROUND(temperature_2m_mean::FLOAT,1) AS mean_temperature,
    ROUND(cloud_cover_mean::FLOAT,1) AS mean_cloud_cover,
    ROUND(leaf_wetness_probability_mean::FLOAT,1) AS mean_leaf_wetness_probability,
    ROUND(precipitation_probability_mean::FLOAT,1) AS mean_precipitation_probability,
    ROUND(relative_humidity_2m_mean::FLOAT,1) AS mean_relative_humidity,
    ROUND(visibility_mean::FLOAT,2) AS mean_visibility,
    ROUND(wind_speed_10m_mean::FLOAT,2) AS mean_wind_speed,
    ROUND(wind_gusts_10m_mean::FLOAT,2) AS mean_wind_gusts,
    ROUND(wind_direction_10m_dominant::FLOAT,1) AS dominant_wind_direction,
    ROUND(uv_index_max::FLOAT,1) AS max_uv_index,
    ROUND(daylight_duration::FLOAT/3600,2) AS daylight_duration,
    ROUND(sunshine_duration::FLOAT/3600,2) AS sunshine_duration,
    ROUND(rain_sum::FLOAT,2) as total_rain,
    ROUND(showers_sum::FLOAT,2) AS total_showers,
    ROUND(snowfall_sum::FLOAT,2) AS total_snowfall,
    ROUND(precipitation_sum::FLOAT,2) AS total_precipitation,
    ROUND(precipitation_hours::FLOAT,2) AS precipitation_hours
FROM
    {{source{'weather','cforecast_src'}}}
