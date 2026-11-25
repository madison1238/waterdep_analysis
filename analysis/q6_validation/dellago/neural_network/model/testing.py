import os
import csv
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

from model import NucleationMLP
from training import load_datasets




MODEL_PATH = "models/best_model.pt"
RESULTS_DIR = "results"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

os.makedirs(RESULTS_DIR, exist_ok=True)

def load_test_data():
    train_loader, validation_loader, test_loader, feature_columns = load_datasets()
    print(f"Using device: {DEVICE}")
    print(f"Number of features: {len(feature_columns)}")
    return test_loader, feature_columns

def load_model(feature_columns):
    checkpoint = torch.load( MODEL_PATH, map_location=DEVICE,weights_only=True)

    if checkpoint["feature_columns"] != feature_columns:
        raise ValueError("Feature columns do not match!")
    model = NucleationMLP(input_features=len(feature_columns)).to(DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print("Model loaded successfully!")
    print(f"Best validation loss: {checkpoint['validation_loss']:.6f}")
    return model

def test_model(model, test_loader):
    all_labels = []
    all_logits = []
    all_probabilities = []
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for features, labels in test_loader:
            features = features.to(DEVICE)
            labels = labels.to(DEVICE).float()

            logits = model(features).reshape(-1)
            loss = F.softplus(-labels * logits).mean()
            probabilities = torch.sigmoid(logits)

            predicted_labels = torch.where(probabilities >= 0.5,1,-1)
            batch_size = labels.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

            all_labels.extend(labels.cpu().numpy())
            all_logits.extend(logits.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())

    all_labels = np.array(all_labels).astype(int)
    all_logits = np.array(all_logits)
    all_probabilities = np.array(all_probabilities)

    predicted_labels = np.where(all_probabilities >= 0.5,1,-1)
    test_loss = total_loss / total_samples
    return (
        all_labels,
        all_logits,
        all_probabilities,
        predicted_labels,
        test_loss
    )


def calculate_auc(labels, probabilities):
    actual = (labels == 1).astype(int)
    positives = np.sum(actual == 1)
    negatives = np.sum(actual == 0)
    if positives == 0 or negatives == 0:
        print("Cannot calculate AUC: test set needs both classes.")
        return np.nan

    sorted_indices = np.argsort(probabilities)
    sorted_probabilities = probabilities[sorted_indices]
    sorted_actual = actual[sorted_indices]
    ranks = np.empty(len(probabilities), dtype=float)
    i = 0
    while i < len(probabilities):
        j = i + 1
        while (j < len(probabilities) and sorted_probabilities[j] == sorted_probabilities[i]):
            j += 1
        average_rank = ((i + 1) + j) / 2
        ranks[sorted_indices[i:j]] = average_rank
        i = j
    positive_rank_sum = np.sum(ranks[actual == 1])
    auc = (positive_rank_sum - positives * (positives + 1) / 2) / (positives * negatives)
    return auc



def calculate_metrics(labels, probabilities, predicted_labels, test_loss):
    tp = np.sum((labels == 1) & (predicted_labels == 1))
    tn = np.sum((labels == -1) & (predicted_labels == -1))
    fp = np.sum((labels == -1) & (predicted_labels == 1))
    fn = np.sum((labels == 1) & (predicted_labels == -1))
    accuracy = (tp + tn) / len(labels)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    f1 = (2 * precision * recall / (precision + recall)if (precision + recall) > 0 else 0.0)
    actual_probabilities = (labels == 1).astype(float)

    brier_score = np.mean((probabilities - actual_probabilities) ** 2)
    auc = calculate_auc(labels, probabilities)

    metrics = {
        "Test Loss": test_loss,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "Brier Score": brier_score,
        "ROC-AUC": auc
    }

    print("\n========== TEST RESULTS ==========")
    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")
    print(f"\nTP: {tp}")
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print("==================================")

    return metrics

def save_predictions(labels, logits, probabilities, predicted_labels):
    output_path = os.path.join(RESULTS_DIR, "test_predictions.csv")
    with open(output_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Actual Label",
            "Actual Outcome",
            "Raw Network Output",
            "Predicted Committor Probability",
            "Predicted Label",
            "Predicted Outcome",
            "Absolute Probability Error"
        ])
        for actual, logit, probability, predicted in zip(
            labels, logits, probabilities, predicted_labels
        ):
            actual_binary = 1 if actual == 1 else 0
            error = abs(probability - actual_binary)

            writer.writerow([
                actual,
                "Nucleation" if actual == 1 else "Melting",
                logit,
                probability,
                predicted,
                "Nucleation" if predicted == 1 else "Melting",
                error
            ])

    print(f"Saved predictions to {output_path}")


def plot_confusion_matrix(labels, predicted_labels):
    tp = np.sum((labels == 1) & (predicted_labels == 1))
    tn = np.sum((labels == -1) & (predicted_labels == -1))
    fp = np.sum((labels == -1) & (predicted_labels == 1))
    fn = np.sum((labels == 1) & (predicted_labels == -1))

    cm = np.array([
        [tn, fp],
        [fn, tp]
    ])

    fig, ax = plt.subplots(figsize=(7, 6))

    image = ax.imshow(cm, cmap="Blues")

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels(["Melting", "Nucleation"])
    ax.set_yticklabels(["Melting", "Nucleation"])

    ax.set_xlabel("Predicted Outcome")
    ax.set_ylabel("Actual Outcome")
    ax.set_title("Test Set Confusion Matrix")
    for i in range(2):
        for j in range(2):
            ax.text(
                j, i, str(cm[i, j]),
                ha="center",
                va="center",
                fontsize=14
            )

    fig.colorbar(image, ax=ax)

    plt.tight_layout()

    plt.savefig(
        os.path.join(RESULTS_DIR, "confusion_matrix.png"),
        dpi=300
    )

    plt.close()

    print("Saved confusion matrix.")


def plot_roc_curve(labels, probabilities):
    actual = (labels == 1).astype(int)
    positives = np.sum(actual == 1)
    negatives = np.sum(actual == 0)
    if positives == 0 or negatives == 0:
        print("Cannot plot ROC curve: test set needs both classes.")
        return

    sorted_indices = np.argsort(-probabilities)
    sorted_actual = actual[sorted_indices]
    sorted_probabilities = probabilities[sorted_indices]
    tpr = [0.0]
    fpr = [0.0]
    tp = 0
    fp = 0
    i = 0

    while i < len(sorted_actual):
        threshold = sorted_probabilities[i]
        j = i
        while j < len(sorted_actual) and sorted_probabilities[j] == threshold:
            if sorted_actual[j] == 1:
                tp += 1
            else:
                fp += 1
            j += 1
        tpr.append(tp / positives)
        fpr.append(fp / negatives)
        i = j
    auc = calculate_auc(labels, probabilities)
    plt.figure(figsize=(7, 6))
    plt.plot(fpr,tpr,label=f"Neural Network (AUC = {auc:.3f})")
    plt.plot([0, 1],[0, 1],linestyle="--",label="Random Classifier")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(os.path.join(RESULTS_DIR, "roc_curve.png"),dpi=300)
    plt.close()
    print("Saved ROC curve.")

def plot_probability_distributions(labels, probabilities):
    nucleation_probs = probabilities[labels == 1]
    melting_probs = probabilities[labels == -1]
    plt.figure(figsize=(8, 6))
    plt.hist(
        melting_probs,
        bins=25,
        alpha=0.6,
        label="Melting",
        density=True
    )
    plt.hist(
        nucleation_probs,
        bins=25,
        alpha=0.6,
        label="Nucleation",
        density=True
    )
    plt.xlabel("Predicted Committor Probability")
    plt.ylabel("Density")
    plt.title("Predicted Probability Distributions")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "probability_distributions.png"),dpi=300)
    plt.close()
    print("Saved probability distributions.")




def plot_calibration(labels, probabilities):
    actual = (labels == 1).astype(int)
    num_bins = 10
    bin_edges = np.linspace(0, 1, num_bins + 1)
    mean_predicted = []
    fraction_positive = []
    for i in range(num_bins):
        if i == num_bins - 1:
            mask = ((probabilities >= bin_edges[i]) &(probabilities <= bin_edges[i + 1]))
        else:
            mask = ((probabilities >= bin_edges[i]) &(probabilities < bin_edges[i + 1]))
        if np.sum(mask) == 0:
            continue
        mean_predicted.append(np.mean(probabilities[mask]))
        fraction_positive.append(np.mean(actual[mask]))
    plt.figure(figsize=(7, 6))
    plt.plot(
        mean_predicted,
        fraction_positive,
        marker="o",
        label="Neural Network"
    )
    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Perfect Calibration"
    )
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Fraction of Nucleation Outcomes")
    plt.title("Probability Calibration")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig( os.path.join(RESULTS_DIR, "calibration_curve.png"),dpi=300)
    plt.close()
    print("Saved calibration curve.")



def main():
    test_loader, feature_columns = load_test_data()
    model = load_model(feature_columns)

    (
        labels,
        logits,
        probabilities,
        predicted_labels,
        test_loss
    ) = test_model(model, test_loader)

    metrics = calculate_metrics(
        labels,
        probabilities,
        predicted_labels,
        test_loss
    )
    metrics_path = os.path.join(RESULTS_DIR,"test_metrics.csv")
    with open(metrics_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        for name, value in metrics.items():
            writer.writerow([name, value])
    save_predictions(labels,logits,probabilities,predicted_labels)

    plot_confusion_matrix(labels, predicted_labels)
    plot_roc_curve(labels, probabilities)
    plot_probability_distributions(labels, probabilities)
    plot_calibration(labels, probabilities)

    print("\nTesting complete!")
    print(f"All results saved in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
