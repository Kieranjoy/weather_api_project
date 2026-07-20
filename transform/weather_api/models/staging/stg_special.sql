SELECT
    TO_DATE(TO_TIMESTAMP_NTZ(load_date::NUMBER/1000000)) AS load_date,
    DATE::TIMESTAMP::DATE AS date,
    soil_moisture_0_to_1cm::FLOAT AS "0_to_1cm_mean_soil_moisture",
    soil_moisture_1_to_3cm::FLOAT AS "1_to_3cm_mean_soil_moisture",
    soil_moisture_3_to_9cm::FLOAT AS "3_to_9cm_mean_soil_moisture",
    soil_temperature_0cm::FLOAT AS "0cm_mean_soil_temperature",
    soil_temperature_6cm::FLOAT AS "6cm_mean_soil_temperature"
FROM
    {{source{'weather','special_src'}}}