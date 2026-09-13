# Data sources and cleaning notes

Downloaded on 2026-09-09 from the official King Fahd International Airport website.

- [Source and reuse terms](https://kfia.sa/open-data)
- [Domestic CSV](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/csv/2024-2025-Open_Data_Domestic.csv)
- [International CSV](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/csv/2024-2025-Open_Data_International.csv)
- [Metadata workbook](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/Meta_Data.xlsx)

The publisher requires attribution with a link and states that users must not alter the data or its source. Preserve raw downloads and clearly document any derived transformations. Refer to the official page for the full terms; no separate license is assigned to these source files here.

## Source observations

- Three empty rows precede the header.
- Empty columns surround the actual data.
- Some headers and category values contain trailing spaces.
- The domestic direction field contains `Departue `.
- Passenger counts contain commas and surrounding spaces.
- Some city names contain unexpected bytes. UTF-8 decoding fails on the domestic file. Latin-1 is used for initial inspection, not as a confirmed interpretation of every character.
- Both files contain months January–December in 2024 and January–October in 2025. This does not prove every city has a record for every month.

## Applied cleaning

Raw files remain unchanged. The notebook records investigation; the cleaning script produces the derived CSV.

- Skip introductory rows, drop empty columns, and trim headers.
- Separate published total rows before aggregating detail records.
- Trim direction, city, and international month text; correct `Departue` to `Departure`.
- Standardize `Abhaÿ` → `Abha`, `Beijingÿ` → `Beijing`, `Bagdad` → `Baghdad`, and `kochi` → `Kochi`.
- Convert numeric columns. Preserve the 16 international `-` passenger values as missing, not zero.
- Add month number, quarter, and a date using the first day as the reporting-month convention.
- Validate keys, required fields, positive reported counts, and source totals before exporting 2,479 rows.

Domestic totals reconcile to 11,557,402 passengers and 83,949 flights. International totals reconcile to 11,652,478 reported passengers and 84,828 flights. Passenger sums exclude missing values. These are traffic counts, not unique travelers. The partial 2025 year should not be compared directly with full-year 2024 totals.
