main_proj_eko_panel
import numpy as np
import pandas as pd
import requests
import time
import zipfile
import eurostat

# %%
#dane baza danych API BDL lokalne polskie wiec jesli dla innyc krajow to musimy wziac z eurostat 
BASE = "https://bdl.stat.gov.pl/api/v1"
#kod do importowania wzialem z chata ale widze ze zaczytalo wszystko ok ;) jakbys mogl spojrzec
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

# teraz idziemy po dane dotyczace emisji CO2 itp z ponizszego linku 

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


geo_col = "Subnational code *"

if geo_col not in edgar.columns:
    raise ValueError(f"Nie znaleziono kolumny '{geo_col}'. Dostępne kolumny: {edgar.columns.tolist()}")

print(f"✓ Znaleziono kolumnę geo: {geo_col}")

# bierzemy tylko dla PL w kolumnie GEO COL

edgar_pl = edgar[
    edgar[geo_col].astype(str).str.startswith("PL", na=False)
].copy()

print(f"Liczba wierszy dla Polski: {edgar_pl.shape[0]}")
print(f"Unikalne kody PL: {sorted(edgar_pl[geo_col].unique())}")

# tutaj filtr dalej na dane lata i kolumny

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

import pandas as pd
import numpy as np

panel = bdl_panel.merge(panel_emisje, on=["geo", "year"], how="left")

# gdp_pl, unemp_pl, pop_pl
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

# %%

#  agregacja danych oraz zostaw tylko obserwacje z kodem POLSKA :) Polska gurom xD 

panel_model = panel.copy()

panel_model = panel_model[
    panel_model["geo"].astype(str).str.match(r"^PL[0-9]{2}$", na=False)
].copy()

# konwersja zmiennych zeby byly numeryczne 
num_cols = [
    "wydatki_dzial_900",
    "oze_produkcja",
    "oze_udzial",
    "produkcja_do_zuzycia_energii",
    "ghg_co2eq",
    "gdp",
    "unemployment",
    "population",
    "wydatki_900_pc",
    "wydatki_900_pc_lag1"
]

for col in num_cols:
    if col in panel_model.columns:
        panel_model[col] = pd.to_numeric(panel_model[col], errors="coerce")

panel_model["emisje_pc"] = panel_model["ghg_co2eq"] / panel_model["population"]


panel_model["gdp_pc"] = panel_model["gdp"] / panel_model["population"]

# logarytmowanie zmiennych log emicje pc i gdp per capita i wydatki gov 
panel_model["log_emisje_pc"] = np.log(panel_model["emisje_pc"])
panel_model["log_gdp_pc"] = np.log(panel_model["gdp_pc"])
panel_model["log_wydatki_900_pc_lag1"] = np.log1p(panel_model["wydatki_900_pc_lag1"])

# sortowanie i duplikaty checking
panel_model = panel_model.sort_values(["geo", "year"])


duplikaty = panel_model.duplicated(["geo", "year"]).sum()
print("Liczba duplikatów geo-year:", dups)

cols_model = [
    "geo",
    "year",
    "log_emisje_pc",
    "log_wydatki_900_pc_lag1",
    "oze_udzial",
    "produkcja_do_zuzycia_energii",
    "log_gdp_pc",
    "unemployment"
]

print(panel_model[cols_model].isna().sum())

# baza finalnaa
panel_est = panel_model[cols_model].dropna().copy()

print(panel_est.shape)
display(panel_est.head())

# %%
### tu modelujemy i robimy tabele opisowa

panel_model = panel.copy()

panel_model["emisje_pc"] = panel_model["ghg_co2eq"] / panel_model["population"]
panel_model["gdp_pc"] = panel_model["gdp"] / panel_model["population"]

panel_model["log_emisje_pc"] = np.log(panel_model["emisje_pc"])
panel_model["log_gdp_pc"] = np.log(panel_model["gdp_pc"])
panel_model["log_wydatki_900_pc_lag1"] = np.log1p(panel_model["wydatki_900_pc_lag1"])

cols_model = [
    "geo",
    "year",
    "log_emisje_pc",
    "log_wydatki_900_pc_lag1",
    "oze_udzial",
    "produkcja_do_zuzycia_energii",
    "log_gdp_pc",
    "unemployment"
]

panel_est = panel_model[cols_model].dropna().copy()

# tabela opisowa
desc = panel_est[
    [
        "log_emisje_pc",
        "log_wydatki_900_pc_lag1",
        "oze_udzial",
        "produkcja_do_zuzycia_energii",
        "log_gdp_pc",
        "unemployment"
    ]
].describe().T

display(desc)

# %%
avg_oze = panel_est.groupby("year", as_index=False)["oze_udzial"].mean()

plt.figure(figsize=(9, 5))
plt.plot(avg_oze["year"], avg_oze["oze_udzial"], marker="o")
plt.title("Średni udział OZE w regionach NUTS2")
plt.xlabel("Rok")
plt.ylabel("Udział OZE")
plt.grid(True)
plt.show()

# %%
plt.figure(figsize=(8, 5))
plt.scatter(
    panel_est["log_wydatki_900_pc_lag1"],
    panel_est["log_emisje_pc"],
    alpha=0.7
)
plt.title("Wydatki środowiskowe a emisje per capita")
plt.xlabel("Log opóźnionych wydatków działu 900 per capita")
plt.ylabel("Log emisji per capita")
plt.grid(True)
plt.show()

# %%
import matplotlib.pyplot as plt

avg_year = panel_est.groupby("year", as_index=False)["log_emisje_pc"].mean()

plt.figure(figsize=(9, 5))
plt.plot(avg_year["year"], avg_year["log_emisje_pc"], marker="o")
plt.title("Średni logarytm emisji per capita)
plt.xlabel("Rok")
plt.ylabel("Średni log emisji per capita")
plt.grid(True)
plt.show()


