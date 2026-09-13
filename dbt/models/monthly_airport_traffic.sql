SELECT
    d.reporting_month,
    SUM(f.passengers) AS total_passengers,
    SUM(f.flights) AS total_flights
FROM public.fact_airport_traffic AS f
JOIN public.dim_date AS d
    ON f.date_key = d.date_key
GROUP BY d.reporting_month
