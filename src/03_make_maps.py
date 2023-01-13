import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx

plt.style.use("src/style.mplstyle")

# Define data path
data_path = "data/processed/domestic_violence_cases.gpkg"
layer_name = "Domestic Violence Cases"
save_images_path = "images/{:02d}_{}_map.{}"

# Define variables of interest
variables = ["DVCper1000iH", "PercentageAdultinPrimary", "WomenperMen"]
titles = ["Domestic violence cases", "% Adults in primary", "Ratio women per men"]
colors = ["YlOrRd", "cool", "Spectral_r"]
save_keys = ["dvc_jenks", "perc_adults_primary_jenks", "ratio_women_per_men"]

def main():
    # Load data
    gdf = gpd.read_file(data_path, layer=layer_name)

    # List to store figures
    figs = []

    # Iterate throught variables for plot them
    for var, title, color in zip(variables, titles, colors):
        # Create figure
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(1, 1, 1)

        # Plot data
        gdf.plot(
            column=var,
            scheme="fisherjenks",
            cmap=color,
            edgecolor="black",
            linewidth=0.25,
            alpha=0.5,
            legend=True,
            legend_kwds={"loc": "upper left", "bbox_to_anchor": (1, 1)},
            ax=ax,
        )

        # Add basemap
        cx.add_basemap(
            ax=ax,
            crs=gdf.crs.to_string(),
            source=cx.providers.Esri.WorldTerrain,
        )

        # Add title and labels
        ax.set(xlabel="Longitude", ylabel="Latitude", title=title)

        # Store figure
        figs.append(fig)

    # Save figures
    for i, (fig, key) in enumerate(zip(figs, save_keys)):
        fig.savefig(save_images_path.format(i+7, key, "png"))

    # Show plots
    # plt.show()

if __name__ == "__main__":
    main()
