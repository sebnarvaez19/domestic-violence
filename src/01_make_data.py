import geopandas as gpd
import numpy as np
import pandas as pd

# Define path to load and save data
census_path = "data/external/national_census/MGN_ANM_MPIOS.shp"
violence_path = "data/external/Reporte_Delito_Violencia_Intrafamiliar_Polic_a_Nacional.csv"
save_path = "data/processed/domestic_violence_cases.gpkg"
layer_name = "Domestic Violence Cases"

def main():
    # Load data
    census = gpd.read_file(census_path)
    violence = pd.read_csv(violence_path)

    # Delete problematic rows
    violence = violence.loc[violence["CODIGO DANE"] != "NO REPORTA", :]

    # Change format of city code column
    census.MPIO_CDPMP = census.MPIO_CDPMP.astype(np.int64)
    violence["CODIGO DANE"] = violence["CODIGO DANE"].astype(np.int64)//1000

    # Get the city names
    cities = violence[["CODIGO DANE", "MUNICIPIO"]].drop_duplicates()

    # Group data by city code
    violence = (
        violence.groupby(by="CODIGO DANE")
        .count()
        .reset_index()
        .iloc[:,[0, 1]]
    )

    # Add the city names
    violence = violence.merge(cities, on="CODIGO DANE", how="left")

    # Rename columns
    violence.columns = ["MPIO_CDPMP", "DomesticViolenceCases", "City"]

    # Merge census data with domestic violance cases
    gdf = census.merge(violence, on="MPIO_CDPMP", how="left")

    # Sort columns
    columns = gdf.columns.to_list()
    columns.remove("geometry")
    columns.append("geometry") 

    gdf = gdf[columns]

    # Calculate domestic violance cases per 1000 inhabitants
    gdf["DVCper1000iH"] = gdf.DomesticViolenceCases/gdf.STP27_PERS*1000

    # Save data
    gdf.to_file(save_path, layer=layer_name)

if __name__ == "__main__":
    main()
