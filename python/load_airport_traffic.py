from pathlib import Path

import pandas as pd
import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "dammam_airport_traffic_clean.csv"
ENV_FILE = PROJECT_ROOT / ".env"


def get_connection():
    settings = {}

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            name, value = line.split("=", maxsplit=1)
            settings[name] = value

    return psycopg.connect(
        host=settings["DB_HOST"],
        port=settings["DB_PORT"],
        dbname=settings["DB_NAME"],
        user=settings["DB_USER"],
        password=settings["DB_PASSWORD"],
    )


def main():
    # Read the combined cleaned CSV.
    traffic = pd.read_csv(
        INPUT_FILE,
        parse_dates=["date"],
        dtype={"passengers": "Int64", "flights": "int64"},
    )

    # Validate the traffic grain before loading.
    business_key = [
        "airport_code",
        "year",
        "month_number",
        "flight_type",
        "direction",
        "city",
    ]
    if traffic.duplicated(subset=business_key).any():
        raise ValueError("The cleaned CSV contains duplicate traffic records.")

    if traffic["flights"].isna().any() or (traffic["flights"] <= 0).any():
        raise ValueError("Flights must be present and greater than zero.")

    if (traffic["passengers"].dropna() <= 0).any():
        raise ValueError("Reported passenger values must be greater than zero.")

    # Build one record for each dimension value.
    date_records = []
    for row in traffic[
        ["date", "year", "quarter", "month_number", "month"]
    ].drop_duplicates().itertuples(index=False):
        date_records.append(
            {
                "reporting_month": row.date.date(),
                "year": int(row.year),
                "quarter": int(row.quarter),
                "month_number": int(row.month_number),
                "month_name": row.month,
            }
        )

    airport_records = []
    for code in traffic["airport_code"].drop_duplicates():
        airport_records.append({"airport_code": code})

    city_records = []
    for city in traffic["city"].drop_duplicates():
        city_records.append({"city_name": city})

    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Insert dimensions first. Existing values are skipped safely.
            cursor.executemany(
                """
                INSERT INTO dim_date (
                    reporting_month, year, quarter, month_number, month_name
                ) VALUES (
                    %(reporting_month)s, %(year)s, %(quarter)s,
                    %(month_number)s, %(month_name)s
                )
                ON CONFLICT (reporting_month) DO NOTHING
                """,
                date_records,
            )

            cursor.executemany(
                """
                INSERT INTO dim_airport (airport_code)
                VALUES (%(airport_code)s)
                ON CONFLICT (airport_code) DO NOTHING
                """,
                airport_records,
            )

            cursor.executemany(
                """
                INSERT INTO dim_city (city_name)
                VALUES (%(city_name)s)
                ON CONFLICT (city_name) DO NOTHING
                """,
                city_records,
            )

            # Get the generated keys needed by the fact table.
            cursor.execute("SELECT reporting_month, date_key FROM dim_date")
            date_keys = dict(cursor.fetchall())

            cursor.execute("SELECT airport_code, airport_key FROM dim_airport")
            airport_keys = dict(cursor.fetchall())

            cursor.execute("SELECT city_name, city_key FROM dim_city")
            city_keys = dict(cursor.fetchall())

            fact_records = []
            for row in traffic.itertuples(index=False):
                fact_records.append(
                    {
                        "date_key": date_keys[row.date.date()],
                        "airport_key": airport_keys[row.airport_code],
                        "city_key": city_keys[row.city],
                        "flight_type": row.flight_type,
                        "direction": row.direction,
                        "passengers": (
                            None if pd.isna(row.passengers) else int(row.passengers)
                        ),
                        "flights": int(row.flights),
                    }
                )

            # Insert new traffic records or update existing ones.
            cursor.executemany(
                """
                INSERT INTO fact_airport_traffic (
                    date_key, airport_key, city_key, flight_type,
                    direction, passengers, flights
                ) VALUES (
                    %(date_key)s, %(airport_key)s, %(city_key)s,
                    %(flight_type)s, %(direction)s, %(passengers)s,
                    %(flights)s
                )
                ON CONFLICT (
                    date_key, airport_key, city_key, flight_type, direction
                ) DO UPDATE SET
                    passengers = EXCLUDED.passengers,
                    flights = EXCLUDED.flights
                """,
                fact_records,
            )

            for table in [
                "dim_date",
                "dim_airport",
                "dim_city",
                "fact_airport_traffic",
            ]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table}: {cursor.fetchone()[0]} rows")

    print("Airport traffic warehouse load completed.")


if __name__ == "__main__":
    main()
