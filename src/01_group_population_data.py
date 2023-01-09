import os
import pandas as pd
from tabula import read_pdf

codes_path = "data/external/Codificación de Municipios por Departamento.pdf"
data_path = "data/external/national_census_data/"
save_path = "data/processed/population.csv"

codes_cols = ["U_DPTO", "U_MPIO", "Departamento", "Municipio"]
pop_data = []

files = os.listdir(data_path)

for f in files:
    df = pd.read_csv(data_path+f)
    df = df.groupby(by=["U_DPTO", "U_MPIO"])[["HA_TOT_PER"]].sum()
    df = df.reset_index()

    pop_data.append(df)

pop_data = pd.concat(pop_data, ignore_index=True)

codes = read_pdf(codes_path, pages="all", pandas_options={"columns": codes_cols})

codes[0] = codes[0][1:]
codes[0].U_DPTO = codes[0].U_DPTO.astype("int64")
codes[0].U_MPIO = codes[0].U_MPIO.astype("int64")

codes = pd.concat(codes, ignore_index=True)

pop_data = pop_data.merge(codes, on=["U_DPTO", "U_MPIO"])

pop_data.to_csv(save_path)