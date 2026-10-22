from ovito.io import import_file
from ovito.modifiers import (
    ClusterAnalysisModifier,
)
import csv
import os
import shutil
import matplotlib.pyplot as plt

#ss_ratios = [100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000]
#temps =  [180,190,200,210,220,230,240]

ss_ratios = [250000]
temps =  [210]

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
    plt.close()

def collect_plots(output):
    os.makedirs(output,exist_ok=True)
    for ss_ratio in ss_ratios:
        for temp in temps:
            if (ss_ratio == 100000) and (temp >= 210):
                continue
            if (ss_ratio == 500000) and (temp < 200):
                continue
            sim_directory = f"sims/ss_{ss_ratio}/temp_{temp}"
            plot_path = f"{sim_directory}/summary/largest_vs_time.png"
            if os.path.exists(plot_path):
                copy_plot_directory = f"{output}/ss_{ss_ratio}"
                os.makedirs(f"{output}/ss_{ss_ratio}", exist_ok=True)
                copy_plot_file = f"{copy_plot_directory}/temp_{temp}.png"
                shutil.copy(plot_path, copy_plot_file)
                print(f"Copied {plot_path} -> {copy_plot_file}")
            else:
                print(f"Could not find {plot_path}")




for ss_ratio in ss_ratios:
    for temp in temps:
        if (ss_ratio == 100000) and (temp >= 210):
            continue
        if (ss_ratio == 500000) and (temp < 200):
            continue
        directory = f"sims/ss_{ss_ratio}/temp_{temp}"
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
collect_plots('figure_2a')