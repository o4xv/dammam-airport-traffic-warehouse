CREATE TABLE dim_date (
    date_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reporting_month DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month_number INTEGER NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    month_name TEXT NOT NULL
);
CREATE TABLE dim_airport (
    airport_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    airport_code TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_city (
    city_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name TEXT NOT NULL UNIQUE
);
CREATE TABLE fact_airport_traffic (
    traffic_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    airport_key INTEGER NOT NULL REFERENCES dim_airport(airport_key),
    city_key INTEGER NOT NULL REFERENCES dim_city(city_key),

    flight_type TEXT NOT NULL
        CHECK (flight_type IN ('Domestic', 'International')),

    direction TEXT NOT NULL
        CHECK (direction IN ('Arrival', 'Departure')),

    passengers INTEGER
        CHECK (passengers > 0),

    flights INTEGER NOT NULL
        CHECK (flights > 0),

    UNIQUE (
        date_key,
        airport_key,
        city_key,
        flight_type,
        direction
    )
);