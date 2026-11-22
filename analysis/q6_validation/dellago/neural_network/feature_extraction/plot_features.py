import csv
import matplotlib.pyplot as plt
import os
import math


INPUT_FILE = "combined_dataset.csv"
OUTPUT_DIR = "feature_plots"

X_COLUMN = "Largest Cluster Size (n)"
LABEL_COLUMN = "outcome"

MELTED_COLOR = "blue"
NUCLEATED_COLOR = "orange"


FEATURES = [
    "Q6",
    "Q4",
    "q6",
    "q4",
    "All Tetrahedrality",
    "Tetrahedrality",
    "nih",
    "nic",
    "nih/n",
    "nic/n",
    "Coordination Number (CN)",
    "CN Standard Deviation",
    "Voronoi Volume",
    "Voronoi Volume Standard Deviation",
    "Radius of Gyration (Rg)",
    "Anisotropy (I)",
    "Acylindricity (J)",
    "Asphericity (K)",
    "E1",
    "E2",
    "E3",
    "E4",
    "E5",
    "E6"
]


melted = {feature: [] for feature in FEATURES}
nucleated = {feature: [] for feature in FEATURES}

with open(INPUT_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        cluster_size = float(row[X_COLUMN])
        outcome = row[LABEL_COLUMN].strip().lower()
        if outcome == "melted":
            dataset = melted
        elif outcome == "nucleated":
            dataset = nucleated
        else:
            continue
        for feature in FEATURES:
            feature_value = float(row[feature])
            dataset[feature].append((cluster_size, feature_value))
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Dataset loaded successfully")
print(f"Melted configurations: {len(next(iter(melted.values())))}")
print(f"Nucleated configurations: {len(next(iter(nucleated.values())))}")
print(f"Total features: {len(FEATURES)}")


for feature in FEATURES:
    plt.figure(figsize=(8, 6))
    plt.scatter(
        [point[0] for point in melted[feature]],
        [point[1] for point in melted[feature]],
        color=MELTED_COLOR,
        label="Melted",
        alpha=0.6,
        s=15
    )

    plt.scatter(
        [point[0] for point in nucleated[feature]],
        [point[1] for point in nucleated[feature]],
        color=NUCLEATED_COLOR,
        label="Nucleated",
        alpha=0.6,
        s=15
    )

    plt.xlabel("Largest Cluster Size (n)")
    plt.ylabel(feature)
    plt.title(f"{feature} vs. Largest Cluster Size")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    filename = feature.replace("/", "_").replace(" ", "_")
    plt.savefig(os.path.join(OUTPUT_DIR, f"{filename}.png"))
    plt.close()



num_features = len(FEATURES)
cols = 5
rows = math.ceil(num_features / cols)
fig, axes = plt.subplots(rows,cols,figsize=(22, 18))
axes = axes.flatten()
for i, feature in enumerate(FEATURES):
    ax = axes[i]

    ax.scatter(
        [point[0] for point in melted[feature]],
        [point[1] for point in melted[feature]],
        color=MELTED_COLOR,
        alpha=0.5,
        s=8,
        label="Melted"
    )

    # Nucleated points
    ax.scatter(
        [point[0] for point in nucleated[feature]],
        [point[1] for point in nucleated[feature]],
        color=NUCLEATED_COLOR,
        alpha=0.5,
        s=8,
        label="Nucleated"
    )

    ax.set_title(feature, fontsize=10)
    ax.set_xlabel("Cluster Size", fontsize=8)
    ax.set_ylabel(feature, fontsize=8)
    ax.grid(alpha=0.2)

# Remove unused subplot spaces
for i in range(num_features, len(axes)):
    fig.delaxes(axes[i])

# Shared legend
handles, labels = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    loc="upper center",
    ncol=2,
    fontsize=11
)

fig.suptitle(
    "Initial Features vs. Largest Cluster Size",
    fontsize=16,
    y=0.99
)

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(
    os.path.join(OUTPUT_DIR, "all_features_combined.png"),
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nAll plots generated successfully!")
print(f"Plots saved in: {OUTPUT_DIR}")