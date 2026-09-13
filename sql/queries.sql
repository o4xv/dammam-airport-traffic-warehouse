-- Monthly Dammam Airport traffic totals.
SELECT
    d.reporting_month,
    SUM(f.passengers) AS total_passengers,
    SUM(f.flights) AS total_flights
FROM fact_airport_traffic AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY d.reporting_month
ORDER BY d.reporting_month;


-- Total traffic by domestic and international flight type.
SELECT
    flight_type,
    SUM(passengers) AS total_passengers,
    SUM(flights) AS total_flights
FROM fact_airport_traffic
GROUP BY flight_type
ORDER BY flight_type;


-- Ten cities with the highest total passenger traffic.
SELECT
    c.city_name,
    SUM(f.passengers) AS total_passengers,
    SUM(f.flights) AS total_flights
FROM fact_airport_traffic AS f
JOIN dim_city AS c
    ON f.city_key = c.city_key
GROUP BY c.city_name
ORDER BY total_passengers DESC
LIMIT 10;


-- Arrival and departure traffic for each flight type.
SELECT
    flight_type,
    direction,
    SUM(passengers) AS total_passengers,
    SUM(flights) AS total_flights
FROM fact_airport_traffic
GROUP BY flight_type, direction
ORDER BY flight_type, direction;
