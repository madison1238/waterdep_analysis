import csv
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


training_file = "train.csv"

excluded_columns = {
    "config_id",
    "trial_id",
    "outcome",
    "label"
}

feature_order = [
    "nih",
    "Largest Cluster Size (n)",
    "E1",
    "Radius of Gyration (Rg)",
    "nic",
    "E2",
    "E4",
    "E5",
    "Anisotropy (I)",
    "CN Standard Deviation",
    "E3",
    "nic/n",
    "Voronoi Volume Standard Deviation",
    "Q4",
    "Q6",
    "E6",
    "Voronoi Volume",
    "Coordination Number (CN)",
    "nih/n",
    "Tetrahedrality",
    "Acylindricity (J)",
    "Asphericity (K)"
]

label_map = {
    "nih": r"$n_{Ih}$",
    "Largest Cluster Size (n)": r"$n$",
    "E1": r"$\varepsilon_1$",
    "Radius of Gyration (Rg)": r"$R_g$",
    "nic": r"$n_{Ic}$",
    "E2": r"$\varepsilon_2$",
    "E4": r"$\varepsilon_4$",
    "E5": r"$\varepsilon_5$",
    "Anisotropy (I)": r"$I$",
    "CN Standard Deviation": r"$C_{\sigma}$",
    "E3": r"$\varepsilon_3$",
    "nic/n": r"$n_{Ic}/n$",
    "Voronoi Volume Standard Deviation": r"$V_{\sigma}$",
    "Q4": r"$Q_4$",
    "Q6": r"$Q_6$",
    "E6": r"$\varepsilon_6$",
    "Voronoi Volume": r"$V_{m}$",
    "Coordination Number (CN)": r"$C_{m}$",
    "nih/n": r"$n_{Ih}/n$",
    "Tetrahedrality": r"$\Theta$",
    "Acylindricity (J)": r"$J$",
    "Asphericity (K)": r"$K$"
}




custom_cmap = LinearSegmentedColormap.from_list(
    "custom_correlation",
    [
        "#042F5D",
        "#2166AC",
        "#4393C3",
        "#92C5DE",
        "#D1E5F0",
        "#F7F7F7",
        "#FDDBC7",
        "#F4A582",
        "#D6604D",
        "#B2182B",
        "#6C0120"  
    ]
)


def pearson(x, y):
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    numerator = sum(
        (a - mean_x) * (b - mean_y)
        for a, b in zip(x, y)
    )

    denominator_x = sum((a - mean_x) ** 2 for a in x)
    denominator_y = sum((b - mean_y) ** 2 for b in y)

    denominator = math.sqrt(denominator_x * denominator_y)

    if denominator == 0:
        return float("nan")
    return numerator / denominator


def create_correlation_plot(show_values, filename):
    fig, ax = plt.subplots(figsize=(17, 14))
    heatmap = ax.imshow(
        correlation_matrix,
        cmap=custom_cmap,
        vmin=-1,
        vmax=1,
        aspect="auto"
    )

    ax.set_xticks(range(num_features))
    ax.set_yticks(range(num_features))

    display_labels = [label_map[feature] for feature in feature_columns]

    ax.set_xticklabels(display_labels, rotation=90, fontsize=30, weight='bold')
    ax.set_yticklabels(display_labels, fontsize=30, weight='bold')

    if show_values:
        for i in range(num_features):
            for j in range(num_features):
                value = correlation_matrix[i][j]

                ax.text(
                    j, i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=6
                )

    colorbar = fig.colorbar(heatmap, ax=ax)
    colorbar.set_label("Correlation",fontsize=40)
    colorbar.ax.tick_params(labelsize=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

    plt.close(fig)




data = {}

with open(training_file, "r", newline="") as file:
    reader = csv.DictReader(file)
    feature_columns = [
        column for column in reader.fieldnames
        if column not in excluded_columns
    ]
    data = {column: [] for column in feature_columns}
    for row in reader:
        for column in feature_columns:
            data[column].append(float(row[column]))

missing = [feature for feature in feature_order if feature not in data]
if missing:
    raise ValueError(f"Missing columns: {missing}")

feature_columns = feature_order
num_features = len(feature_columns)
correlation_matrix = []
for feature1 in feature_columns:
    row = []
    for feature2 in feature_columns:
        correlation = pearson(data[feature1], data[feature2])
        row.append(correlation)
    correlation_matrix.append(row)


create_correlation_plot(
    show_values=True,
    filename="pearson_correlation_matrix_labeled.png"
)

create_correlation_plot(
    show_values=False,
    filename="pearson_correlation_matrix_unlabeled.png"
)