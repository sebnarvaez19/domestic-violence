import numpy as np
import geopandas as gpd
import pandas as pd

# Define paths
data_path = "data/processed/domestic_violences_cases.csv"
shp_path = "data/shapefiles/cities/cities.shp"
save_path = "data/processed/domestic_violences_cases.gpkg"
layer_name = "Domestic Violences Cases"

# Define columns names
columns = [
    "Departamento", "Municipio", "MpCodigo", "Population", 
    "DomesticViolenceCases", "CasesPer1000Habitants", "geometry"
]

def main():
    # Load data
    violences = pd.read_csv(data_path, index_col=0)

    # Create code column
    violences["MpCodigo"] = violences.U_DPTO*1000 + violences.U_MPIO
    violences = violences.drop(["U_DPTO", "U_MPIO"], axis=1)

    # Load shapefile
    gdf = gpd.read_file(shp_path)
    gdf = gdf[["MpCodigo", "geometry"]]                 # Filter columns of interest

    # Change type of codes column
    gdf.MpCodigo = gdf.MpCodigo.astype(np.int64)        

    # Merge data
    gdf = gdf.merge(violences, on="MpCodigo", how="left")

    # Sort columns
    gdf = gdf[columns]

    # Fill NaNs with zero
    gdf = gdf.fillna(0)

    # Save data
    gdf.to_file(save_path, layer=layer_name)

if __name__ == "__main__":
    main()