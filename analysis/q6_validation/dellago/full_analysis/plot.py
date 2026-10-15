import csv
import matplotlib.pyplot as plt


def plot_MFPT_v_n(save_file):
    n_values = []
    mfpt_values = []
    with open("../summary/MFPT.csv", "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            n = int(row["n"])
            if row["MFPT_ps"] == "":
                continue
            mfpt = float(row["MFPT_ps"])
            n_values.append(n)
            mfpt_values.append(mfpt)
    plt.figure(figsize=(8, 6))
    plt.plot(
        n_values,
        mfpt_values,
        marker="o",
        markersize=4,)

    plt.xlabel("Cluster size, n")
    plt.ylabel("MFPT (ps)")
    plt.xlim(5, 60)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_file)