
import torch
import torch.nn.functional as F
import torch.optim as optim

from pathlib import Path

from model import NucleationMLP
from dataset import load_datasets


BATCH_SIZE = 16
EPOCHS = 100
LEARNING_RATE = 1e-2

torch.manual_seed(42)

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

def calculate_loss(predictions, labels):
    loss = F.softplus(-labels * predictions)
    return loss.sum()

def train_one_epoch(model, train_loader, optimizer, device):
    model.train()
    total_loss = 0.0
    total_samples = 0
    for X_batch, y_batch in train_loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        optimizer.zero_grad()

        predictions = model(X_batch)

        loss = calculate_loss(predictions, y_batch)

        loss.backward()

        optimizer.step()

        batch_size = X_batch.size(0)
        total_loss += loss.item() * batch_size

        total_samples += batch_size
    average_loss = total_loss / total_samples
    return average_loss

def validate(model, validation_loader, device):
    model.eval()
    total_loss = 0.0
    total_samples = 0
    with torch.no_grad():
        for X_batch, y_batch in validation_loader:

            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            predictions = model(X_batch)

            loss = calculate_loss(predictions, y_batch)

            batch_size = X_batch.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size
    average_loss = total_loss / total_samples

    return average_loss


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}",flush=True)

    train_loader, validation_loader, test_loader, feature_columns = (load_datasets())

    print(f"Number of features: {len(feature_columns)}",flush=True)
    print(f"Training samples: {len(train_loader.dataset)}",flush=True)
    print(f"Validation samples: {len(validation_loader.dataset)}",flush=True)

    model = NucleationMLP(input_features=len(feature_columns)).to(device)

    optimizer = optim.Adam( model.parameters(),lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=EPOCHS,eta_min=1e-6)

    best_validation_loss = float("inf")
    model_path = MODEL_DIR / "best_model.pt"
    print("\nStarting training...\n",flush=True)

    for epoch in range(EPOCHS):

        training_loss = train_one_epoch(model,train_loader,optimizer,device)

        validation_loss = validate( model,validation_loader,device)

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch [{epoch + 1}/{EPOCHS}]"
            f"Training Loss: {training_loss:.6f} "
            f"Validation Loss: {validation_loss:.6f} "
            f"LR: {current_lr:.7f}",
            flush=True
        )

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            torch.save(
                {
                    "epoch": epoch + 1,
                    "model_state_dict": model.state_dict(),
                    "validation_loss": validation_loss,
                    "feature_columns": feature_columns
                },
                model_path
            )

            print("  Saved new best model!",flush=True)
        scheduler.step()

    print("\nTraining complete!")
    print(f"Best validation loss: {best_validation_loss:.6f}")
    print(f"Best model saved to: {model_path}")


if __name__ == "__main__":
    main()
