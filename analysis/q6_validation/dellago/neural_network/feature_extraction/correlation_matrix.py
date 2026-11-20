import csv
import math
import matplotlib.pyplot as plt

training_file = "training.csv"

excluded_columns = {
    "config_id",
    "trial_id",
    "outcome",
    "label"
}

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

num_features = len(feature_columns)
correlation_matrix = []
for feature1 in feature_columns:
    row = []
    for feature2 in feature_columns:
        correlation = pearson(data[feature1], data[feature2])
        row.append(correlation)
    correlation_matrix.append(row)


fig, ax = plt.subplots(figsize=(17, 14))
heatmap = ax.imshow(
    correlation_matrix,
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    aspect="auto"
)

ax.set_xticks(range(num_features))
ax.set_yticks(range(num_features))

ax.set_xticklabels(feature_columns, rotation=90, fontsize=9)
ax.set_yticklabels(feature_columns, fontsize=9)

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
colorbar.set_label("Pearson Correlation Coefficient", fontsize=11)
ax.set_title("Pearson Correlation Matrix", fontsize=16, pad=15)
plt.tight_layout()
plt.savefig("pearson_correlation_matrix.png", dpi=300)
plt.show()