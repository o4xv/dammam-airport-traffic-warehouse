from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMESTIC_FILE = PROJECT_ROOT / "data" / "raw" / "2024-2025-Open_Data_Domestic.csv"
INTERNATIONAL_FILE = (
    PROJECT_ROOT / "data" / "raw" / "2024-2025-Open_Data_International.csv"
)
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "dammam_airport_traffic_clean.csv"

MONTH_NUMBERS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

FINAL_COLUMNS = [
    "airport_code",
    "date",
    "year",
    "quarter",
    "month_number",
    "month",
    "flight_type",
    "direction",
    "city",
    "passengers",
    "flights",
]

KEY_COLUMNS = [
    "airport_code",
    "year",
    "month_number",
    "flight_type",
    "direction",
    "city",
]


def read_source(file_path):
    data = pd.read_csv(file_path, skiprows=3, encoding="latin-1")
    data = data.dropna(axis=1, how="all")
    data.columns = data.columns.str.strip()

    source_total = data[data["Arrival/Departure"].isna()].copy()
    data = data[data["Arrival/Departure"].notna()].copy()

    return data, source_total


def add_date_columns(data):
    data["month_number"] = data["month"].map(MONTH_NUMBERS)
    data["date"] = pd.to_datetime(
        data["year"].astype(str) + "-" + data["month"],
        format="%Y-%b",
    )
    data["quarter"] = data["date"].dt.quarter

    return data


def source_total(source_total_row, column_name):
    value = source_total_row[column_name].iloc[0]
    return int(value.strip().replace(",", ""))


def clean_domestic():
    domestic, domestic_total = read_source(DOMESTIC_FILE)

    domestic["Arrival/Departure"] = (
        domestic["Arrival/Departure"].str.strip().replace({"Departue": "Departure"})
    )
    domestic["Destination_City"] = (
        domestic["Destination_City"].str.strip().replace({"Abhaÿ": "Abha"})
    )

    domestic = domestic.rename(
        columns={
            "Airport IATA": "airport_code",
            "Year": "year",
            "Type": "flight_type",
            "Month": "month",
            "Arrival/Departure": "direction",
            "Destination_City": "city",
            "Pax": "passengers",
            "ATMs": "flights",
        }
    )

    domestic["year"] = domestic["year"].astype("int64")
    domestic["passengers"] = (
        domestic["passengers"].str.strip().str.replace(",", "", regex=False).astype("int64")
    )
    domestic["flights"] = domestic["flights"].str.strip().astype("int64")

    domestic = add_date_columns(domestic)[FINAL_COLUMNS]

    assert domestic.shape == (674, 11)
    assert domestic.isna().sum().sum() == 0
    assert domestic.duplicated(subset=KEY_COLUMNS).sum() == 0
    assert (domestic["passengers"] > 0).all()
    assert (domestic["flights"] > 0).all()
    assert domestic["passengers"].sum() == source_total(domestic_total, "Pax")
    assert domestic["flights"].sum() == source_total(domestic_total, "ATMs")
    assert set(domestic["flight_type"]) == {"Domestic"}

    return domestic


def clean_international():
    international, international_total = read_source(INTERNATIONAL_FILE)

    international["Arrival/Departure"] = international["Arrival/Departure"].str.strip()
    international["Destination_City"] = international["Destination_City"].str.strip()
    international["Destination_City"] = international["Destination_City"].replace(
        {
            "Bagdad": "Baghdad",
            "Beijingÿ": "Beijing",
            "kochi": "Kochi",
        }
    )

    international = international.rename(
        columns={
            "Airport IATA": "airport_code",
            "Year": "year",
            "Type": "flight_type",
            "Month": "month",
            "Arrival/Departure": "direction",
            "Destination_City": "city",
            "Pax": "passengers",
            "ATMs": "flights",
        }
    )

    international["month"] = international["month"].str.strip()
    international["year"] = international["year"].astype("int64")
    international["passengers"] = (
        international["passengers"]
        .str.strip()
        .str.replace(",", "", regex=False)
        .replace("-", pd.NA)
        .astype("Int64")
    )
    international["flights"] = (
        international["flights"]
        .str.strip()
        .str.replace(",", "", regex=False)
        .astype("int64")
    )

    international = add_date_columns(international)[FINAL_COLUMNS]

    assert international.shape == (1805, 11)
    assert international.duplicated(subset=KEY_COLUMNS).sum() == 0
    assert international["passengers"].isna().sum() == 16
    assert international["flights"].isna().sum() == 0
    assert (international["passengers"].dropna() > 0).all()
    assert (international["flights"] > 0).all()
    assert international["passengers"].sum() == source_total(international_total, "Pax")
    assert international["flights"].sum() == source_total(international_total, "ATMs")
    assert set(international["flight_type"]) == {"International"}

    return international


def main():
    domestic = clean_domestic()
    international = clean_international()

    traffic = pd.concat([domestic, international], ignore_index=True)

    assert traffic.shape == (2479, 11)
    assert traffic.duplicated(subset=KEY_COLUMNS).sum() == 0
    assert traffic["passengers"].isna().sum() == 16
    assert traffic["flights"].isna().sum() == 0
    assert traffic.drop(columns="passengers").isna().sum().sum() == 0
    assert set(traffic["airport_code"]) == {"DMM"}
    assert set(traffic["direction"]) == {"Arrival", "Departure"}
    assert (traffic["passengers"].dropna() > 0).all()
    assert (traffic["flights"] > 0).all()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    traffic.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Saved {len(traffic)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
