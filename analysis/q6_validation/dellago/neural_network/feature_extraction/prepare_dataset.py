import csv
import json
import math
import random
from collections import Counter, defaultdict



INPUT_FILE = "combined_dataset.csv"

TRAIN_FILE = "train.csv"
VALIDATION_FILE = "validation.csv"
TEST_FILE = "test.csv"

SCALING_FILE = "feature_scaling.json"

RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15

EXPECTED_TRIALS_PER_CONFIG = 10


feature_columns = [
    "Largest Cluster Size (n)",
    "Q6",
    "Q4",
    "Tetrahedrality",
    "nih",
    "nih/n",
    "nic/n",
    "Coordination Number (CN)",
    "CN Standard Deviation",
    "Voronoi Volume",
    "Voronoi Volume Standard Deviation",
    "lambda 1",
    "lambda 2",
    "lambda 3",
    "Anisotropy (I)",
    "Acylindricity (J)",
    "Asphericity (K)",
    "E2",
    "E3",
    "E4",
    "E5",
    "E6"
]

identifier_columns = ["config_id", "trial_id"]

target_column = "outcome"

label_mapping = {
    "melted": -1,
    "nucleated": 1
}

output_columns = (
    identifier_columns
    + feature_columns
    + [target_column, "label"]
)



with open(INPUT_FILE, "r", newline="") as file:

    reader = csv.DictReader(file)

    required_columns = (
        identifier_columns
        + feature_columns
        + [target_column]
    )

    missing_columns = [
        column for column in required_columns
        if column not in reader.fieldnames
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in input CSV: {missing_columns}"
        )

    rows = list(reader)


if not rows:
    raise ValueError("The input dataset is empty.")



config_groups = defaultdict(list)
config_features = {}
seen_trials = set()

for row in rows:

    config_id = row["config_id"].strip()
    trial_id = row["trial_id"].strip()

    if not config_id or not trial_id:
        raise ValueError("Found a missing configuration or trial ID.")

    trial_key = (config_id, trial_id)

    if trial_key in seen_trials:
        raise ValueError(f"Duplicate trial found: {trial_key}")

    seen_trials.add(trial_key)
    outcome = row[target_column].strip().lower()

    if outcome not in label_mapping:
        raise ValueError(
            f"Unexpected outcome '{outcome}' in {trial_key}"
        )

    row[target_column] = outcome
    row["label"] = label_mapping[outcome]

    current_features = {}

    for column in feature_columns:

        try:
            value = float(row[column])
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid value for '{column}' in {trial_key}"
            )

        if not math.isfinite(value):
            raise ValueError(
                f"Non-finite value for '{column}' in {trial_key}"
            )

        current_features[column] = value
        row[column] = value
    if config_id in config_features:

        for column in feature_columns:

            if not math.isclose(
                current_features[column],
                config_features[config_id][column],
                rel_tol=1e-9,
                abs_tol=1e-12
            ):
                raise ValueError(
                    f"Inconsistent initial feature '{column}' "
                    f"for {config_id}"
                )

    else:
        config_features[config_id] = current_features

    config_groups[config_id].append(row)




for config_id, trials in config_groups.items():

    if len(trials) != EXPECTED_TRIALS_PER_CONFIG:
        raise ValueError(
            f"{config_id} has {len(trials)} trials; "
            f"expected {EXPECTED_TRIALS_PER_CONFIG}."
        )


config_ids = list(config_groups.keys())

rng = random.Random(RANDOM_SEED)
rng.shuffle(config_ids)

total_configs = len(config_ids)

train_count = int(total_configs * TRAIN_RATIO)
validation_count = int(total_configs * VALIDATION_RATIO)

train_configs = set(config_ids[:train_count])

validation_configs = set(
    config_ids[train_count:train_count + validation_count]
)

test_configs = set(
    config_ids[train_count + validation_count:]
)


train_rows = []
validation_rows = []
test_rows = []

for config_id, trials in config_groups.items():

    if config_id in train_configs:
        train_rows.extend(trials)

    elif config_id in validation_configs:
        validation_rows.extend(trials)

    else:
        test_rows.extend(trials)



feature_means = {}
feature_stds = {}

for column in feature_columns:

    values = [row[column] for row in train_rows]

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2 for value in values
    ) / len(values)

    std = math.sqrt(variance)

    if std == 0:
        std = 1.0
        print(f"Warning: {column} has zero variance.")

    feature_means[column] = mean
    feature_stds[column] = std


for dataset in [train_rows, validation_rows, test_rows]:

    for row in dataset:

        for column in feature_columns:

            row[column] = (
                row[column] - feature_means[column]
            ) / feature_stds[column]



datasets = [
    (TRAIN_FILE, train_rows),
    (VALIDATION_FILE, validation_rows),
    (TEST_FILE, test_rows)
]

for filename, dataset in datasets:

    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=output_columns
        )

        writer.writeheader()

        writer.writerows([
            {column: row[column] for column in output_columns}
            for row in dataset
        ])



scaling_parameters = {
    "feature_columns": feature_columns,
    "means": feature_means,
    "standard_deviations": feature_stds,
    "random_seed": RANDOM_SEED
}

with open(SCALING_FILE, "w") as file:
    json.dump(scaling_parameters, file, indent=4)




print("\nDATASET PREPARATION SUMMARY")
print("=" * 45)

for name, dataset, configs in [
    ("Training", train_rows, train_configs),
    ("Validation", validation_rows, validation_configs),
    ("Testing", test_rows, test_configs)
]:

    outcomes = Counter(row[target_column] for row in dataset)

    labels = Counter(row["label"] for row in dataset)

    print(f"\n{name} Dataset")
    print(f"  Configurations: {len(configs)}")
    print(f"  Trials: {len(dataset)}")
    print(f"  Nucleated (+1): {labels[1]}")
    print(f"  Melted (-1): {labels[-1]}")

print("\n" + "=" * 45)
print(f"Total configurations: {total_configs}")
print(f"Total trajectories: {len(rows)}")
print("\nDataset preparation complete!")
