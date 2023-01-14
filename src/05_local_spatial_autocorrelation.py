import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as cx

from numpy.random import seed
from pysal.explore import esda
from pysal.lib import weights
from splot import esda as esdaplot

plt.style.use("src/style.mplstyle")

# Define path and variable of interest
data_path = "data/processed/domestic_violence_cases.gpkg"
layer_name = "Domestic Violence Cases"
save_images_path = "images/{:02d}_{}.{}"

# Define significance
sig = 0.05

def main():
    # Read data, reproject and get the variable of interest
    gdf = gpd.read_file(data_path, layer=layer_name).to_crs(32618)
    gdf = gdf.loc[:, ["City", "DVCper1000iH", "geometry"]]
    
    # Define weights for spatial autocorrelation
    w = weights.KNN.from_dataframe(gdf, k=8)    # k=8 for Queens neighbors
    w.transform = "R"                           # for continuous variable

    # Caculate LISA
    lisa = esda.moran.Moran_Local(gdf.DVCper1000iH, w)

    # Plot local Moran's I
    fig1, ax = plt.subplots(1)
    sns.kdeplot(lisa.Is, shade=True, ax=ax)
    sns.rugplot(lisa.Is, color="red", ax=ax)
    ax.set_xlabel("Moran's I")

    # Plot correlation quadrant
    fig2, axs = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(8, 4))
    
    for s, title, ax in zip((1, sig), ("All correlation", "Significant correlations"), axs):
        esdaplot.lisa_cluster(
            lisa,
            gdf,
            p=s,
            legend_kwds=dict(loc=4, fontsize=8, frameon=True),
            ax=ax,
        )

        ax.set_title(title)

    # Find what are the significant cities
    gdf["p_value"] = lisa.p_sim
    gdf["sig"] = 1 * (gdf.p_value < sig)

    # Set quadrant labels
    gdf["spot"] = lisa.q * gdf.sig
    gdf["quadrant"] = gdf.spot.map({0: "ns", 1: "HH", 2: "LH", 3: "LL", 4: "HL"})

    # Print classified
    print(gdf.quadrant.value_counts())

    # Print all cities in HH quadrant
    hh = (
        gdf.loc[gdf.quadrant == "HH", ["City", "DVCper1000iH"]]
           .sort_values("DVCper1000iH", ascending=False)
    )

    print(hh)

    # Plot all cities in HH quadrant
    fig3, ax = plt.subplots(1, figsize=(6, 4), tight_layout=True)

    ax.bar(
        x=hh.City,
        height=hh.DVCper1000iH,
        color="red",
        alpha=0.7,
    )

    ax.set_xticklabels(ax.get_xticklabels(), fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("DV cases per 1000 inhabitants")

    # Save figures
    figs = [fig1, fig2, fig3]
    labs = ["local_moran_I", "correlation_quadrant", "dvc_per_1000_HH_cities"]
    formats = ["svg", "png", "svg"]

    for i, (fig, lab, f) in enumerate(zip(figs, labs, formats)):
        fig.savefig(save_images_path.format(i+13, lab, f))

if __name__ == "__main__":
    main()
