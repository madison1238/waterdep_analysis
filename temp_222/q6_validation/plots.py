import matplotlib.pyplot as plt
import config
import os
import csv
from ovito.modifiers import ChillPlusModifier

def plot_largest_vs_time(filename, save):
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        time_ps = []
        largest_cluster = []
        for row in reader:
            time = float(row["timestep"]) * 0.005
            cluster_size = int(row["largest_cluster"])
            time_ps.append(time)
            largest_cluster.append(cluster_size)


    plt.figure(figsize=(8, 5))
    plt.plot(time_ps, largest_cluster)
    plt.xlabel("Time (ps)")
    plt.ylabel("Largest Cluster Size")
    plt.title("Largest Cluster Size vs. Time")
    plt.tight_layout()
    plt.savefig(save)
    