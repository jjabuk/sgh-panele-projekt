# %%
import numpy as np
import pandas as pd
import requests
import time
import zipfile
import eurostat

# %%
# Pobierz listę zmiennych z API BDL
BASE = "https://bdl.stat.gov.pl/api/v1"

# Pobierz pierwszą stronę zmiennych
response = requests.get(f"{BASE}/variables?lang=pl&format=json&page=0&pageSize=50")
variables_data = response.json()

# Wyświetl dostępne zmienne
print(f"Całkowita liczba zmiennych: {variables_data.get('totalRecords', 0)}\n")
print("Pierwsze 50 zmiennych:\n")

for var in variables_data.get("results", [])[:20]:  # Pokaż tylko 20
    print(f"ID: {var.get('id')}, Nazwa: {var.get('name', 'brak nazwy')}")

# %%
BASE = "https://bdl.stat.gov.pl/api/v1"

def get_bdl_variable(var_id, years, unit_level=3, name="variable"):
    rows = []

    for year in years:
        params = {
            "year": year,
            "unitLevel": unit_level,
            "page": 0,
            "pageSize": 100,
            "format": "json",
            "lang": "pl"
        }

        url = f"{BASE}/data/by-variable/{var_id}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for item in data.get("results", []):
            unit_id = item.get("id") or item.get("unitId")
            unit_name = item.get("name") or item.get("unitName")

            for value in item.get("values", []):
                rows.append({
                    "unit_id_bdl": unit_id,
                    "region_name": unit_name,
                    "year": int(value.get("year", year)),
                    name: value.get("val")
                })

        time.sleep(0.25)  # żeby nie uderzać w limity API

    return pd.DataFrame(rows)

years = range(2008, 2025)

wydatki_900 = get_bdl_variable(
    var_id=152670,
    years=years,
    unit_level=3,
    name="wydatki_dzial_900"
)

oze_prod = get_bdl_variable(
    var_id=194886,
    years=range(2008, 2025),
    unit_level=3,
    name="oze_produkcja"
)

oze_share = get_bdl_variable(
    var_id=288086,
    years=range(2008, 2025),
    unit_level=3,
    name="oze_udzial"
)

energia_ratio = get_bdl_variable(
    var_id=454054,
    years=range(2008, 2025),
    unit_level=3,
    name="produkcja_do_zuzycia_energii"
)


# %%
import eurostat
import pandas as pd

def eurostat_to_long(code):
    df = eurostat.get_data_df(code, flags=False)
    time_cols = [c for c in df.columns if str(c).isdigit()]
    id_cols = [c for c in df.columns if c not in time_cols]

    long = df.melt(
        id_vars=id_cols,
        value_vars=time_cols,
        var_name="year",
        value_name="value"
    )

    long["year"] = long["year"].astype(int)
    return long

gdp_raw = eurostat_to_long("nama_10r_2gdp")
unemp_raw = eurostat_to_long("tgs00010")
pop_raw = eurostat_to_long("demo_r_d2jan")


print(gdp_raw.columns)

# %%
def get_geo_col(df):
    for c in df.columns:
        if "geo" in c.lower():
            return c
    raise ValueError("Nie znaleziono kolumny geo")

geo_gdp = get_geo_col(gdp_raw)
geo_unemp = get_geo_col(unemp_raw)
geo_pop = get_geo_col(pop_raw)

gdp_pl = gdp_raw[
    gdp_raw[geo_gdp].astype(str).str.startswith("PL")
].copy()

unemp_pl = unemp_raw[
    unemp_raw[geo_unemp].astype(str).str.startswith("PL")
].copy()

pop_pl = pop_raw[
    pop_raw[geo_pop].astype(str).str.startswith("PL")
].copy()

# %%
from functools import reduce

bdl_frames = [wydatki_900, oze_prod, oze_share, energia_ratio]

bdl_panel = reduce(
    lambda left, right: pd.merge(
        left, right,
        on=["unit_id_bdl", "region_name", "year"],
        how="outer"
    ),
    bdl_frames
)

# %%
nuts_map = {
    "REGION DOLNOŚLĄSKIE": "PL51",
    "REGION KUJAWSKO-POMORSKIE": "PL61",
    "REGION LUBELSKIE": "PL81",
    "REGION LUBUSKIE": "PL43",
    "REGION ŁÓDZKIE": "PL71",
    "REGION MAŁOPOLSKIE": "PL21",
    "REGION OPOLSKIE": "PL52",
    "REGION PODKARPACKIE": "PL82",
    "REGION PODLASKIE": "PL84",
    "REGION POMORSKIE": "PL63",
    "REGION ŚLĄSKIE": "PL22",
    "REGION ŚWIĘTOKRZYSKIE": "PL72",
    "REGION WARMIŃSKO-MAZURSKIE": "PL62",
    "REGION WIELKOPOLSKIE": "PL41",
    "REGION ZACHODNIOPOMORSKIE": "PL42",
    "REGION WARSZAWSKI STOŁECZNY": "PL91",
    "REGION MAZOWIECKI REGIONALNY": "PL92",
}

bdl_panel["region_clean"] = (
    bdl_panel["region_name"]
    .str.upper()
    .str.replace("  ", " ", regex=False)
    .str.strip()
)

bdl_panel["geo"] = bdl_panel["region_clean"].map(nuts_map)

# %%
import pandas as pd
import requests
import zipfile
import io
import re

# --- 1. Pobranie EDGAR ---

url = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/subnational_NUTS2/2025_FT2024_GHG_NUTS2/EDGAR_2025_GHGs_CO2eq_AR5_NUTS2_by_country_sector_1990-2024_b.zip"

response = requests.get(url)
response.raise_for_status()

z = zipfile.ZipFile(io.BytesIO(response.content))
data_file = z.namelist()[0]

print("Wczytuję:", data_file)

# Czytaj zakladkę "Fossil CO2", header w wierszu 7 (indeks 6)
edgar = pd.read_excel(z.open(data_file), engine="openpyxl", sheet_name="Fossil CO2", header=6)

print("EDGAR shape:", edgar.shape)
print("Kolumny EDGAR:")
print(edgar.columns.tolist())

# --- 2. Znalezienie kolumny z kodem NUTS2 (Subnational code w kolumnie D) ---

geo_col = "Subnational code *"

if geo_col not in edgar.columns:
    raise ValueError(f"Nie znaleziono kolumny '{geo_col}'. Dostępne kolumny: {edgar.columns.tolist()}")

print(f"✓ Znaleziono kolumnę geo: {geo_col}")

# --- 3. Zostaw tylko polskie NUTS2 (kody zaczynające się od "PL") ---

edgar_pl = edgar[
    edgar[geo_col].astype(str).str.startswith("PL", na=False)
].copy()

print(f"Liczba wierszy dla Polski: {edgar_pl.shape[0]}")
print(f"Unikalne kody PL: {sorted(edgar_pl[geo_col].unique())}")

# --- 4. Znalezienie kolumn lat 1990-2024 ---

year_cols = []

for col in edgar_pl.columns:
    col_str = str(col).replace("Y_", "").strip()
    if col_str.isdigit():
        year = int(col_str)
        if 1990 <= year <= 2024:
            year_cols.append(col)

if len(year_cols) == 0:
    raise ValueError("Nie znaleziono kolumn z latami 1990-2024.")

print(f"Znalezione lata: {sorted([int(str(c).replace('Y_', '')) for c in year_cols])}")

# --- 5. Zamiana wide -> long ---

df_long = edgar_pl.melt(
    id_vars=[geo_col],
    value_vars=year_cols,
    var_name="year",
    value_name="ghg_co2eq"
)

df_long = df_long.rename(columns={geo_col: "geo"})

df_long["geo"] = df_long["geo"].astype(str)
df_long["year"] = (
    df_long["year"]
    .astype(str)
    .str.replace("Y_", "", regex=False)
    .astype(int)
)

df_long["ghg_co2eq"] = pd.to_numeric(df_long["ghg_co2eq"], errors="coerce")

# --- 6. Zakres lat do analizy ---

df_long = df_long[
    (df_long["year"] >= 2008) &
    (df_long["year"] <= 2024)
].copy()

# --- 7. Suma emisji po sektorach dla regionu NUTS2 i roku ---

panel_emisje = (
    df_long
    .groupby(["geo", "year"], as_index=False)["ghg_co2eq"]
    .sum(min_count=1)
)

print("\n✓ panel_emisje gotowe:")
display(panel_emisje.head(10))
print(f"Shape: {panel_emisje.shape}")
print(f"Regiony: {sorted(panel_emisje['geo'].unique())}")

# %%
# przykład: upewnij się, że w EDGAR masz kolumny geo i year

import pandas as pd
import numpy as np

# --- N
panel = bdl_panel.merge(panel_emisje, on=["geo", "year"], how="left")

# po przygotowaniu gdp_pl, unemp_pl, pop_pl jako geo-year-value:
gdp_panel = gdp_pl.rename(columns={geo_gdp: "geo", "value": "gdp"})[
    ["geo", "year", "gdp", "unit"]
]

unemp_panel = unemp_pl.rename(columns={geo_unemp: "geo", "value": "unemployment"})[
    ["geo", "year", "unemployment"]
]

pop_panel = pop_pl.rename(columns={geo_pop: "geo", "value": "population"})[
    ["geo", "year", "population"]
]

panel = (
    panel
    .merge(gdp_panel, on=["geo", "year"], how="left")
    .merge(unemp_panel, on=["geo", "year"], how="left")
    .merge(pop_panel, on=["geo", "year"], how="left")
)

panel.to_csv("panel_zielona_transformacja_nuts2_PL.csv", index=False)

# %%
panel["wydatki_900_pc"] = panel["wydatki_dzial_900"] / panel["population"]
panel["log_ghg"] = np.log(panel["ghg_co2eq"])
panel["log_gdp"] = np.log(panel["gdp"])

panel = panel.sort_values(["geo", "year"])
panel["wydatki_900_pc_lag1"] = panel.groupby("geo")["wydatki_900_pc"].shift(1)


