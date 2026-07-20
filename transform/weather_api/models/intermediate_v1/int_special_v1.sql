WITH hourly_variables AS (
SELECT
    TO_DATE(TO_TIMESTAMP_NTZ(load_date::NUMBER/1000000)) AS load_date,
    DATE::TIMESTAMP::DATE AS date,
    ROUND(((soil_moisture_0_to_1cm::FLOAT + soil_moisture_1_to_3cm::FLOAT + soil_moisture_3_to_9cm::FLOAT)/3),2) AS "0_to_9cm_mean_soil_moisture",
    ROUND(((soil_temperature_0cm::FLOAT + soil_temperature_6cm::FLOAT)/2),2) AS "0_to_6cm_mean_soil_temperature"
FROM
    {{ref{'stg_special'}}}
)
SELECT
    load_date,
    date,
    ROUND(AVG("0_to_9cm_mean_soil_moisture"),2) AS "0_to_9cm_mean_soil_moisture",
    ROUND(AVG("0_to_6cm_mean_soil_temperature"),2) AS "0_to_6cm_mean_temperature"
FROM 
    hourly_variables
GROUP BY 
    1,2

    -- no semicolons
