import numpy as np
import pandas as pd

violence_path = "data/external/Reporte_Delito_Violencia_Intrafamiliar_Polic_a_Nacional.csv"
population_path = "data/processed/population.csv"
save_path = "data/processed/domestic_violences_cases.csv"

columns = [
    "U_DPTO", "U_MPIO", "DomesticViolenceCases", 
    "Population", "Municipio", "Departamento"
]

def main():
    # Load domestic violence cases data
    vio = pd.read_csv(violence_path)
    
    # Delete problematic rows
    vio = vio.iloc[:-8,:]
    vio = vio.loc[vio["CODIGO DANE"] != "NO REPORTA",:]
    
    # Convert CODIGO DANE to int
    vio["CODIGO DANE"] = vio["CODIGO DANE"].astype(np.int64)//1000
    
    # Calculete the Departamento and Municipio code
    vio["U_DPTO"] = vio["CODIGO DANE"]//1000
    vio["U_MPIO"] = vio["CODIGO DANE"]%1000

    # Group Departamento and Municipio code and sum all cases
    vio = (
        vio.groupby(by=["U_DPTO", "U_MPIO"])
        .sum()
        .reset_index()
        .drop("CODIGO DANE", axis=1)
    )

    # Load population data
    pop = pd.read_csv(population_path, index_col=0)

    # Merge domestic violence cases with population data
    vio = vio.merge(pop, on=["U_DPTO", "U_MPIO"])

    # Replace column names
    vio.columns = columns

    # Calculate domestic violence cases per 100 inhabitants
    vio["CasesPer1000Habitants"] = vio.DomesticViolenceCases/vio.Population*1000

    # Save data
    vio.to_csv(save_path)

if __name__ == "__main__":
    main()