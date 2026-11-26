import csv
import json
from pathlib import Path
import torch
from torch.utils.data import TensorDataset, DataLoader


BATCH_SIZE = 16
DATA_DIR = Path(__file__).resolve().parent


def load_features(filename, feature_columns):
    features = []
    labels = []
    file_path = DATA_DIR / filename
    with open(file_path, "r", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = feature_columns + ["label"]
        missing_columns = [
            column for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"{filename} is missing columns: {missing_columns}"
            )

        for row in reader:
            feature_values = [float(row[column]) for column in feature_columns]
            label = int(row["label"])
            if label not in (-1, 1):
                raise ValueError(
                    f"Invalid label {label} found in {filename}"
                )

            features.append(feature_values)
            labels.append(label)

    X = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    return TensorDataset(X, y)


def load_datasets():
    scaling_path = DATA_DIR / "feature_scaling.json"
    with open(scaling_path, "r") as file:
        scaling_data = json.load(file)
    feature_columns = scaling_data["feature_columns"]
    if len(feature_columns) != 22:
        raise ValueError(
            f"Expected 22 features, but found {len(feature_columns)}"
        )
    train_dataset = load_features("train.csv", feature_columns)
    validation_dataset = load_features("validation.csv", feature_columns)
    test_dataset = load_features("test.csv", feature_columns)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        drop_last=True
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )
    return train_loader, validation_loader, test_loader, feature_columns

if __name__ == "__main__":

    train_loader, validation_loader, test_loader, feature_columns = (load_datasets())
    print("Dataset loading successful!")
    print()
    print(f"Number of input features: {len(feature_columns)}")
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(validation_loader.dataset)}")
    print(f"Test samples: {len(test_loader.dataset)}")
    X_batch, y_batch = next(iter(train_loader))
    print()
    print("Training batch test:")
    print(f"Feature shape: {X_batch.shape}")
    print(f"Label shape: {y_batch.shape}")
    print(f"Labels: {y_batch}")
    print()
    print("Features being used:")
    for feature in feature_columns:
        print(feature)