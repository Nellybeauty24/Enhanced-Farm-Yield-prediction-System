import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


DATA_PATH = "data/nigeria_agri_yield_enhanced.csv"
OUT_DIR = "dataset_visualizations"


def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, name), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved {name}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    sns.set_theme(
        style="whitegrid",
        rc={
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "grid.alpha": 0.35,
        },
    )

    plt.figure(figsize=(11, 6))
    order = df["crop_type"].value_counts().index
    sns.countplot(data=df, x="crop_type", order=order, hue="crop_type", palette="crest", legend=False)
    plt.title("Dataset Crop Distribution")
    plt.xlabel("Crop Type")
    plt.ylabel("Number of Records")
    plt.xticks(rotation=35, ha="right")
    savefig("01_crop_distribution.png")

    plt.figure(figsize=(11, 6))
    region_order = df["region"].value_counts().index
    sns.countplot(data=df, x="region", order=region_order, hue="region", palette="mako", legend=False)
    plt.title("Dataset Regional Coverage")
    plt.xlabel("Region")
    plt.ylabel("Number of Records")
    plt.xticks(rotation=25, ha="right")
    savefig("02_region_distribution.png")

    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x="crop_type", y="yield_kg_ha", hue="crop_type", palette="flare", legend=False)
    plt.title("Yield Distribution by Crop Type")
    plt.xlabel("Crop Type")
    plt.ylabel("Yield (kg/ha)")
    plt.xticks(rotation=35, ha="right")
    savefig("03_yield_by_crop_boxplot.png")

    plt.figure(figsize=(10, 6))
    sns.histplot(df["yield_kg_ha"], bins=40, kde=True, color="#2A9D8F")
    plt.title("Overall Yield Distribution")
    plt.xlabel("Yield (kg/ha)")
    plt.ylabel("Frequency")
    savefig("04_yield_distribution.png")

    numeric_cols = [
        "soil_pH",
        "soil_nitrogen",
        "soil_phosphorus",
        "soil_potassium",
        "rainfall_mm",
        "temperature_C",
        "humidity",
        "yield_kg_ha",
    ]
    corr = df[numeric_cols].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", center=0, square=True, cbar_kws={"shrink": 0.8})
    plt.title("Numeric Feature Correlation Matrix")
    savefig("05_numeric_correlation_heatmap.png")

    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        data=df.sample(n=min(5000, len(df)), random_state=42),
        x="rainfall_mm",
        y="yield_kg_ha",
        hue="crop_type",
        alpha=0.65,
        s=35,
        palette="tab10",
    )
    plt.title("Rainfall vs Yield by Crop")
    plt.xlabel("Rainfall (mm)")
    plt.ylabel("Yield (kg/ha)")
    plt.legend(title="Crop", bbox_to_anchor=(1.02, 1), loc="upper left")
    savefig("06_rainfall_vs_yield.png")

    nutrient_means = (
        df.groupby("crop_type")[["soil_nitrogen", "soil_phosphorus", "soil_potassium"]]
        .mean()
        .reset_index()
        .melt(id_vars="crop_type", var_name="Nutrient", value_name="Average Level")
    )
    plt.figure(figsize=(12, 7))
    sns.barplot(data=nutrient_means, x="crop_type", y="Average Level", hue="Nutrient", palette="viridis")
    plt.title("Average Soil Nutrient Levels by Crop")
    plt.xlabel("Crop Type")
    plt.ylabel("Average Soil Nutrient Value")
    plt.xticks(rotation=35, ha="right")
    plt.legend(title="Nutrient")
    savefig("07_average_nutrients_by_crop.png")

    plt.figure(figsize=(12, 7))
    agro_yield = df.groupby(["agro_zone", "crop_type"], as_index=False)["yield_kg_ha"].mean()
    pivot = agro_yield.pivot(index="agro_zone", columns="crop_type", values="yield_kg_ha")
    sns.heatmap(pivot, cmap="YlGnBu", annot=False, cbar_kws={"label": "Average Yield (kg/ha)"})
    plt.title("Average Yield by Agro Zone and Crop")
    plt.xlabel("Crop Type")
    plt.ylabel("Agro Zone")
    savefig("08_agro_zone_crop_yield_heatmap.png")

    print(f"Dataset visualizations saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
