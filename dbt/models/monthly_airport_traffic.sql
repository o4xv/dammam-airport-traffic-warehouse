SELECT
    d.reporting_month,
    SUM(f.passengers) AS total_passengers,
    SUM(f.flights) AS total_flights
FROM {{ source('airport_warehouse', 'fact_airport_traffic') }} AS f
JOIN {{ source('airport_warehouse', 'dim_date') }} AS d
    ON f.date_key = d.date_key
GROUP BY d.reporting_month
