
import requests
import pandas as pd
from datetime import date

    

import requests
import pandas as pd
import requests
import pandas as pd

def _suiv_month_id(series):
    """Calcule YYYYMM du mois précédent pour une série month_id (int ou str)."""
    s = series.astype(str).str[:6]                     # 'YYYYMM'
    dt = pd.to_datetime(s + "01", format="%Y%m%d")
    suiv= (dt.dt.to_period("M") + 1).dt.strftime("%Y%m")
    return suiv.astype(int)

def fetch_frankfurter_monthly(start="2022-12-31", end="2024-11-30", base="USD"):
    periode = pd.period_range(start=start, end=end, freq="M")
    all_data = {}
    for period in periode:
        date_str = period.end_time.strftime("%Y-%m-%d")
        url = f"https://api.frankfurter.app/{date_str}?from={base}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        all_data[date_str] = data.get("rates", {})
    df = pd.DataFrame.from_dict(all_data, orient="index").sort_index()    
    df.index = pd.to_datetime(df.index)
    df["month_id"] = df.index.strftime("%Y%m")
    df["month_id_join"] = _suiv_month_id(df["month_id"])
    df = df.drop(columns=["month_id"])
    return df

# Exemple d'appel
taux_change=fetch_frankfurter_monthly()

taux_change.to_csv("taux_usd_frankfurter_2023_2024.csv", encoding="utf-8")

#ùatières première 
#conda install -c conda-forge fredapi 
from fredapi import Fred

import pandas as pd
from fredapi import Fred

API_KEY = "18d3910fdbd24f7de83bd9a76e06b400"
fred = Fred(api_key=API_KEY)

# Dictionnaire : Nom lisible -> Code FRED
# (Tu peux ajouter ce que tu veux, voir https://fred.stlouisfed.org/)
FRED_SERIES = {
    # Énergie (daily)
    "Crude Oil (WTI)": "DCOILWTICO",        # WTI (USD/baril)
    "Brent Oil": "DCOILBRENTEU",            # Brent (USD/baril)
    "Natural Gas (Henry Hub)": "DHHNGSP",   # Gaz naturel spot US (USD/MMBtu)

    # Métaux industriels (IMF, monthly)
    "Copper": "PCOPPUSDM",
    "Aluminum": "PALUMUSDM",
    "Nickel": "PNICKUSDM",
    "Zinc": "PZINCUSDM",
    "Tin": "PTINUSDM",
    "Lead": "PLEADUSDM",
    "Iron Ore": "PIORECRUSDM",

    # Agriculture (IMF, monthly)
    "Wheat": "PWHEAMTUSDM",
    "Corn": "PMAIZMTUSDM",
    "Soybeans": "PSOYBUSDM",
    "Rice (Thailand)": "PRICENPQUSDM",
    "Coffee (Arabica - Other Mild)": "PCOFFOTMUSDM",
    "Cocoa": "PCOCOUSDM",
    "Sugar No.11 (World)": "PSUGAISAUSDM",
    "Cotton": "PCOTTINDUSDM",
}
def fetch_fred_monthly(series_dict,start="2022-12-31", end="2024-11-30"):
    all_data = []
    for name, code in series_dict.items():
        # Récupérer la série quotidienne
        s = fred.get_series(code, observation_start=start, observation_end=end)
        s = s.to_frame(name=name)

        # Passer en fin de mois
        s = s.resample("M").last()

        all_data.append(s)

    # Concaténer toutes les séries
    df = pd.concat(all_data, axis=1)

    # Ajouter month_id
    df["month_id"] = df.index.strftime("%Y%m")
    cols = ["month_id"] + [c for c in df.columns if c != "month_id"]
    df = df[cols].reset_index(drop=True)
    df["month_id_join"] = _suiv_month_id(df["month_id"])
    df = df.drop(columns=["month_id"])


    return df
matieres_premiere= fetch_fred_monthly(FRED_SERIES)

import os
os.chdir("C:/Users/cheik/OneDrive/Bureau/CF/ai4trade")

china_2023=pd.read_csv("resultats\donnees\china_2023_finale.csv")
china_2024=pd.read_csv("resultats\donnees\china_2024_finale.csv")
USA_2023=  pd.read_csv("resultats\donnees\\USA_2023_finale.csv")
USA_2024=pd.read_csv("resultats\donnees\\USA_2024_finale.csv")

tables = {
    "USA_2023": USA_2023,
    "USA_2024": USA_2024,
    "china_2023": china_2023,
    "china_2024": china_2024
}
# Boucle principale
tables_finales = {}
for name, tab in tables.items():
    tab=tab.merge(taux_change,  left_on="month_id",right_on="month_id_join", how="left").drop(columns="month_id_join")
    tables_finales[f"{name}_vf"]=tab.merge(matieres_premiere,  left_on="month_id",right_on="month_id_join", how="left").drop(columns="month_id_join")
    tables_finales[f"{name}_vf"].to_csv(f"resultats/donnees/donnees_interne_et_externe/{name}_vf.csv", index=False, encoding="utf-8")