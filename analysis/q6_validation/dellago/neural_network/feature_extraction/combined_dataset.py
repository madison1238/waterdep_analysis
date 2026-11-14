import csv

initial_features_file = "initial_features.csv"
simulation_outcomes_file = "simulation_outcomes.csv"
output_file = "combined_dataset.csv"

initial_features = {}
with open(initial_features_file, "r", newline="") as file:
    reader = csv.DictReader(file)
    feature_columns = reader.fieldnames
    if "config_id" not in feature_columns:
        raise ValueError("Initial features CSV is missing config_id.")
    for row in reader:
        config_id = row["config_id"]
        if config_id in initial_features:
            raise ValueError(f"Duplicate config_id in initial features: {config_id}")
        initial_features[config_id] = row

with open(simulation_outcomes_file, "r", newline="") as file:
    reader = csv.DictReader(file)
    outcome_columns = reader.fieldnames
    if "config_id" not in outcome_columns:
        raise ValueError("Simulation outcomes CSV is missing config_id.")
    output_columns = feature_columns + [
        column for column in outcome_columns if column != "config_id"
    ]

    combined_rows = []
    missing_configs = set()
    for outcome in reader:
        config_id = outcome["config_id"]
        if config_id not in initial_features:
            missing_configs.add(config_id)
            continue
        combined_row = initial_features[config_id].copy()
        for column in outcome_columns:
            if column != "config_id":
                combined_row[column] = outcome[column]
        combined_rows.append(combined_row)


if missing_configs:
    raise ValueError(
        f"Missing initial features for configurations: {sorted(missing_configs)}"
    )

with open(output_file, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=output_columns)
    writer.writeheader()
    writer.writerows(combined_rows)

print(f"Combined dataset created: {output_file}")
print(f"Total rows: {len(combined_rows)}")
print(f"Total configurations: {len(initial_features)}")
