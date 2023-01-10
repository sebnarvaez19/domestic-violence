import os
import pandas as pd
from tabula import read_pdf

# Path to load and save data
codes_path = "data/external/Codificación de Municipios por Departamento.pdf"
data_path = "data/external/national_census_data/"
save_path = "data/processed/population.csv"

# Columns for codes dataset
codes_cols = ["U_DPTO", "U_MPIO", "Municipio", "Departamento"]

def main():
    # List to store all population datasets
    pop_data = []

    # Get the names of all population datasets
    files = os.listdir(data_path)

    # For each files, read it, group data by municipio and departamento and sum it
    for f in files:
        df = pd.read_csv(data_path+f)
        df = df.groupby(by=["U_DPTO", "U_MPIO"])[["HA_TOT_PER"]].sum()
        df = df.reset_index()

        # Add data to population list
        pop_data.append(df)

    # Convert list in a dataframe
    pop_data = pd.concat(pop_data, ignore_index=True)

    # Load all codes and define the column names
    codes = read_pdf(codes_path, pages="all", pandas_options={"columns": codes_cols})

    # Delete first row and change the dtype of the code columns of first dataframe
    codes[0] = codes[0][1:]
    codes[0].U_DPTO = codes[0].U_DPTO.astype("int64")
    codes[0].U_MPIO = codes[0].U_MPIO.astype("int64")

    # Merge all codes dataframes
    codes = pd.concat(codes, ignore_index=True)

    # Add the departamentos and municipios to population data
    pop_data = pop_data.merge(codes, on=["U_DPTO", "U_MPIO"])

    # Change format of titles
    pop_data.Municipio = pop_data.Municipio.map(lambda x: x.capitalize())
    pop_data.Departamento = pop_data.Departamento.map(lambda x: x.capitalize())
    pop_data.Municipio = pop_data.Municipio.map(lambda x: x.replace("\r", " "))
    pop_data.Departamento = pop_data.Departamento.map(lambda x: x.replace("\r", " "))

    # Remove repeated row
    pop_data = pop_data.loc[pop_data.Municipio !=  "Santafe de bogota d.c.- usaquen",:]

    # Save population data
    pop_data.to_csv(save_path)

if __name__ == "__main__":
    main()