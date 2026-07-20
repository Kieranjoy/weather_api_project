SELECT
    *
FROM
    {{ref{'int_cforecast_v1'}}} as c
JOIN 
    {{ref{'int_special_v1'}}} as s
    on c.load_date=s.load_date 
    AND c.date = s.date