import csv
import random
from pathlib import Path

import numpy as np
import torch
import torch.optim as optim

from model import NucleationMLP
from dataset import load_datasets
from training import train_one_epoch, validate




NUM_MODELS = 10
EPOCHS = 100
LEARNING_RATE = 1e-2

SEEDS = [42, 123, 456, 789, 1011,1213, 1415, 1617, 1819, 2021]
BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_model(model_number, seed):
    print("\n" + "=" * 50)
    print(f"TRAINING MODEL {model_number}/{NUM_MODELS}")
    print(f"Random seed: {seed}")
    print("=" * 50, flush=True)

    set_seed(seed)
    train_loader, validation_loader, test_loader, feature_columns = (load_datasets())

    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(validation_loader.dataset)}")
    print(f"Features: {len(feature_columns)}")

    model = NucleationMLP(input_features=len(feature_columns)).to(DEVICE)
    optimizer = optim.Adam(model.parameters(),lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=EPOCHS,eta_min=1e-6)
    best_validation_loss = float("inf")
    model_path = MODEL_DIR / f"model_{model_number:02d}.pt"
    training_losses = []
    validation_losses = []
    learning_rates = []

    for epoch in range(EPOCHS):
        training_loss = train_one_epoch(model,train_loader,optimizer,DEVICE)
        validation_loss = validate(model,validation_loader,DEVICE)
        current_lr = optimizer.param_groups[0]["lr"]
        training_losses.append(training_loss)
        validation_losses.append(validation_loss)
        learning_rates.append(current_lr)

        print(
            f"Model {model_number} | "
            f"Epoch [{epoch + 1}/{EPOCHS}] | "
            f"Train: {training_loss:.6f} | "
            f"Validation: {validation_loss:.6f} | "
            f"LR: {current_lr:.7f}",
            flush=True
        )

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch + 1,
                    "seed": seed,
                    "validation_loss": validation_loss,
                    "feature_columns": feature_columns
                },
                model_path
            )
            print("  Saved new best model!", flush=True)
        scheduler.step()

    history_path = ( RESULTS_DIR /f"model_{model_number:02d}_history.csv")
    with open(history_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Epoch",
            "Training Loss",
            "Validation Loss",
            "Learning Rate"
        ])
        for epoch in range(EPOCHS):
            writer.writerow([
                epoch + 1,
                training_losses[epoch],
                validation_losses[epoch],
                learning_rates[epoch]
            ])
    print(f"\nModel {model_number} complete!")
    print(f"Best validation loss: {best_validation_loss:.6f}")
    print(f"Saved to: {model_path}")
    return {
        "Model": model_number,
        "Seed": seed,
        "Best Validation Loss": best_validation_loss,
        "Best Model Path": str(model_path)
    }

def main():
    print(f"Using device: {DEVICE}")
    print(f"Training {NUM_MODELS} neural networks")
    results = []
    for model_number, seed in enumerate(SEEDS, start=1):
        result = train_model(model_number, seed)
        results.append(result)

    summary_path = RESULTS_DIR / "ensemble_training_summary.csv"

    with open(summary_path, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Model",
                "Seed",
                "Best Validation Loss",
                "Best Model Path"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 50)
    print("ENSEMBLE TRAINING COMPLETE")
    print("=" * 50)

    for result in results:

        print(
            f"Model {result['Model']}: "
            f"Validation Loss = "
            f"{result['Best Validation Loss']:.6f}"
        )

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
