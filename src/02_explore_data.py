import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

from functions.stats_utils import plot_corr_matrix

plt.style.use("src/style.mplstyle")

# Define paths
data_path = "data/processed/domestic_violence_cases.gpkg"
layer_name = "Domestic Violence Cases"
save_image_path = "images/{:02d}_{}.{}"

# Define variables of interest
x_vars = [
    "PercentageAdultinPrimary", 
    "PercentageLSL", 
    "PercentageHWES", 
    "PercentageHWWS",
    "WomenperMen"
]

x_vars_titles = {
    "PercentageAdultinPrimary": "\% Adult in primary",
    "PercentageLSL": "\% Houses in lowest SL",
    "PercentageHWES": "\% Houses without Electric S",
    "PercentageHWWS": "\% Houses without Water S",
    "WomenperMen": "Ratio of women per men"
}

def main():
    # Load data
    gdf = gpd.read_file(data_path, layer=layer_name)

    # Plot top ten most populated cities
    fig1 = plt.figure(tight_layout=True)
    ax = fig1.add_subplot(1, 1, 1)

    ax.bar(
        x=gdf.sort_values("STP27_PERS", ascending=False).City.iloc[:10],
        height=(
            gdf.sort_values("STP27_PERS", ascending=False)
               .STP27_PERS
               .iloc[:10]
        ),
        alpha=0.7
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_ylabel("Population")

    # Plot top ten most violent cities
    fig2 = plt.figure(tight_layout=True)
    ax = fig2.add_subplot(1, 1, 1)

    ax.bar(
        x=gdf.sort_values("DomesticViolenceCases", ascending=False).City.iloc[:10],
        height=(
            gdf.sort_values("DomesticViolenceCases", ascending=False)
               .DomesticViolenceCases
               .iloc[:10]
        ),
        alpha=0.7
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_ylabel("Domestic violence cases")

    # Plot population against domestic violence cases
    fig3 = plt.figure(tight_layout=True)
    ax = fig3.add_subplot(1, 1, 1)

    ax.scatter(
        x=gdf.STP27_PERS,
        y=gdf.DomesticViolenceCases,
        alpha=0.2,
        label="Cities"
    )

    ax.set(xlabel="Population", ylabel="Domestic violence cases")
    ax.set_yscale("log")
    ax.set_xscale("log")

    # Plot top ten most violent cities by population
    fig4 = plt.figure(tight_layout=True)
    ax = fig4.add_subplot(1, 1, 1)

    ax.bar(
        x=gdf.sort_values("DVCper1000iH", ascending=False).City.iloc[:10],
        height=(
            gdf.sort_values("DVCper1000iH", ascending=False)
               .DVCper1000iH
               .iloc[:10]
        ),
        alpha=0.7
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_ylabel("DV cases per 1000 inhabitants")

    # Plot correlation of variables with DV cases per 1000 inhabitants
    fig5, axs = plt.subplots(2, 3, sharey=True, figsize=(8, 5), tight_layout=True)
    axs = axs.reshape(-1)

    for i, (var, ax) in enumerate(zip(x_vars, axs)):
        sns.regplot(
            x=var, 
            y="DVCper1000iH", 
            data=gdf, 
            scatter_kws={"color": "gray", "alpha": 0.2}, 
            ax=ax
        )
        ax.set_ylim(-2, 22)
        ax.set_xlabel(x_vars_titles[var])
        ax.set_ylabel(None)

        if i in (0, 3):
            ax.set_ylabel("DV cases per 1000 inhabitants")

        axs[-1].set_axis_off()

    # Plot correlation matrix
    fig6 = plt.figure(figsize=(5, 5), tight_layout=True)
    ax = fig6.add_subplot(1, 1, 1)

    plot_corr_matrix(gdf, x_vars+["DVCper1000iH"], True, True, ax=ax)

    # Save plots
    figs = [fig1, fig2, fig3, fig4, fig5, fig6]
    labs = [
        "population", "domestic_violence_cases", "population_vs_dvc",
        "dvc_per_1000", "pairs_plot_dvc_per_1000", "corr_dvc_per_1000"
    ]

    for i, (fig, lab) in enumerate(zip(figs, labs)):
        fig.savefig(save_image_path.format(i+1, lab, "svg"))

    # Show plots
    plt.show()

if __name__ == "__main__":
    main()
