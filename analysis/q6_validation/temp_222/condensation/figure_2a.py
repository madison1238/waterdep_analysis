
from ovito.io import import_file
from ovito.modifiers import (
    ClusterAnalysisModifier,
)
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

folders = ["mW", "ml_mW"]
ss_ratios = ['s_1e4','s_5e4','s_1e5' ]

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


for folder in folders:
    for ratio in ss_ratios:
        directory = f"{folder}/{ratio}"
        dump = f"{directory}/dumps/dump.combined.lammpstrj"
        output_dir = f"{directory}/summary"

        pipeline = import_file(dump)
        print("Frames:", pipeline.source.num_frames, flush=True)
        pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,sort_by_size=True))

        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/ice_clusters.csv"
        save_file = f"{output_dir}/largest_vs_time.png"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "frame",
                "timestep",
                "num_clusters",
                "largest_cluster",
            ])

            for frame in range(pipeline.source.num_frames):
                data = pipeline.compute(frame)

                num_clusters = int(data.attributes.get("ClusterAnalysis.cluster_count",0))
                largest_cluster = int(data.attributes.get("ClusterAnalysis.largest_size",0))
                timestep = int(data.attributes["Timestep"])

                
                writer.writerow([
                    frame,
                    timestep,
                    num_clusters,
                    largest_cluster
                ])

                print(
                    f"Frame {frame:3d} | ",
                    f"Timestep {timestep:8d} | ",
                    f"Clusters {num_clusters:4d} | ",
                    f"Largest {largest_cluster:4d} | ",
                    flush=True)
        plot_largest_vs_time(output_file,save_file)