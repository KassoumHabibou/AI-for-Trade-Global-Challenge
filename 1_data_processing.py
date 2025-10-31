############################################### creation tables finales #######################################################################
globals().clear()
import pandas as pd
import os
os.chdir("C:/Users/cheik/OneDrive/Bureau/CF/ai4trade")

code_hs4 = pd.read_excel("données externes/code hs4.xlsx",dtype={"product_id_hs4": str})

china_2023= pd.read_csv("ForParticipants/trade_s_chn_m_hs_2023.csv/trade_s_chn_m_hs_2023.csv",dtype={"product_id": str} )
china_2024= pd.read_csv("ForParticipants/trade_s_chn_m_hs_2024.csv/trade_s_chn_m_hs_2024.csv",dtype={"product_id": str} )
USA_2023= pd.read_csv("ForParticipants/trade_s_usa_state_m_hs_2023.csv/trade_s_usa_state_m_hs_2023.csv",dtype={"product_id": str} )
USA_2024= pd.read_csv("ForParticipants/trade_s_usa_state_m_hs_2024.csv/trade_s_usa_state_m_hs_2024.csv",dtype={"product_id": str} )
tables = {
    "USA_2023": USA_2023,
    "USA_2024": USA_2024,
    "china_2023": china_2023,
    "china_2024": china_2024
}


hs4_name = dict(zip(code_hs4["product_id_hs4"], code_hs4["product_name_hs4"]))

def preparation_table(tab):
    base_cols = ["month_id", "trade_flow_name", "country_id", "country_name", "product_id", "trade_value"]
    tab = tab[base_cols].copy()

    tab["product_id_hs4"] = tab["product_id"].astype(str).str[:4]

    grp_cols = ["month_id","trade_flow_name", "country_id", "country_name", "product_id_hs4"]
    g = (tab.groupby(grp_cols, as_index=False, sort=False)["trade_value"]
             .sum())

    nb_prod = (g.groupby(["month_id", "country_name","country_id"])["product_id_hs4"]
                 .nunique()
                 .rename("nb_product")
                 .reset_index())

    g = g.merge(nb_prod, on=["month_id", "country_name","country_id"], how="left")

    g = g[g["nb_product"] > 200]

    g["product_name_hs4"] = g["product_id_hs4"].map(hs4_name)

    return g

# Boucle principale
tables_finales = {}
for i, (name, tab) in enumerate(tables.items(), start=1):
    tables_finales[f"{name}_finale"] = preparation_table(tab)
    tables_finales[f"{name}_finale"].to_csv(f"resultats/donnees/{name}_finale.csv", index=False, encoding="utf-8")


usa_2023_finale=tables_finales["USA_2023_finale"]
usa_2024_finale=tables_finales["USA_2024_finale"]
china_2023_finale=tables_finales["china_2023_finale"]
china_2024_finale=tables_finales["china_2024_finale"]
