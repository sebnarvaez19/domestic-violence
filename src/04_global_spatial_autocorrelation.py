import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as cx

from numpy.random import seed
from pysal.explore import esda
from pysal.lib import weights

plt.style.use("src/style.mplstyle")

# Define path and variable of interest
data_path = "data/processed/domestic_violence_cases.gpkg"
layer_name = "Domestic Violence Cases"
save_images_path = "images/{:02d}_{}.{}"

def main():
    # Read data, reproject and get the variable of interest
    gdf = gpd.read_file(data_path, layer=layer_name).to_crs(32618)
    gdf = gdf.loc[:, ["DVCper1000iH", "geometry"]]
    
    # Define weights for spatial autocorrelation
    w = weights.Queen.from_dataframe(gdf)
    w.transform = "R"                           # for continuous variable

    # Calculate lagged variable
    gdf["DVCper1000iHLag"] = weights.spatial_lag.lag_spatial(w, gdf.DVCper1000iH)
    
    # Plot variable and lagged variable
    fig1, axs = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(8, 4))
    
    for var, ax in zip(["DVCper1000iH", "DVCper1000iHLag"], axs):
        gdf.plot(
            column=var,
            scheme="quantiles",
            k=5,
            cmap="Spectral_r",
            edgecolor="black",
            alpha=0.5,
            linewidth=0.1,
            legend=True,
            legend_kwds=dict(loc=4, fontsize=8, frameon=True),
            ax=ax,
        )

        cx.add_basemap(
            ax=ax,
            crs=gdf.crs.to_string(),
            source=cx.providers.CartoDB.VoyagerNoLabels,
        )
        
        ax.set_title(var)
        ax.axis("off")

    # Test moran
    m = esda.moran.Moran(gdf.DVCper1000iH, w)
    print(f"Moran's I: {m.I:0.3f} (p-value: {m.p_sim:0.3f})")

    # Standardize variables
    gdf["DVCper1000iH_std"] = gdf.DVCper1000iH - gdf.DVCper1000iH.mean()
    gdf["DVCper1000iHLag_std"] = gdf.DVCper1000iHLag - gdf.DVCper1000iHLag.mean()

    # Plot autocorrelation
    fig2, ax = plt.subplots(1)

    ax.axvline(0, color="black", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.5)

    sns.regplot(
        x="DVCper1000iH_std",
        y="DVCper1000iHLag_std",
        data=gdf,
        scatter_kws=dict(color="gray", alpha=0.5),
        ax=ax,
    )

    # Plot Moran's I
    fig3, ax = plt.subplots(1)

    sns.kdeplot(m.sim, shade=True, ax=ax)
    ax.axvline(m.EI, color="black")
    ax.axvline(m.I, color="red")

    ax.set_xlabel("Moran's I")

    figs = [fig1, fig2, fig3]
    labs = ["lagged_map", "moran_autocorrelation", "moran_I"]
    formats = ["png", "svg", "svg"]

    for i, (fig, lab, f) in enumerate(zip(figs, labs, formats)):
        fig.savefig(save_images_path.format(i+10, lab, f))
    return None

if __name__ == "__main__":
    main()