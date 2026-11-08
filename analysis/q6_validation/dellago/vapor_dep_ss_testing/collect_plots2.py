# instead of making unique plot for every ss ratio and temp each ss ratio will have one plot with all temps displayed
from ovito.io import import_file
from ovito.modifiers import (
    ClusterAnalysisModifier,
)
import csv
import os
import shutil
import matplotlib.pyplot as plt

ss_ratios = [200000, 250000, 300000]
temps =  [180,190,200,210,220,230,240]



def plot_largest_vs_time(ss_ratio, save):
    plt.figure(figsize=(8, 5))
    for temp in temps:
        filename = f"sims/ss_{ss_ratio}/temp_{temp}/summary/ice_clusters.csv"
        if not os.path.exists(filename):
            print(f"Could not find {filename}")
            continue
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            time_ps = []
            largest_cluster = []
            for row in reader:
                time = float(row["timestep"]) * 0.005
                cluster_size = int(row["largest_cluster"])
                time_ps.append(time)
                largest_cluster.append(cluster_size)
        plt.plot(
            time_ps,
            largest_cluster,
            label=f"{temp} K"
        )
    plt.xlabel("Time (ps)", fontsize=12)
    plt.ylabel("Largest Cluster Size", fontsize=12)
    plt.title(f"Largest Ice Cluster Size vs. Time (SS = {ss_ratio})", fontsize=13)
    plt.legend(title="Temperature", fontsize=12)
    plt.tight_layout()
    plt.savefig(save, dpi=300)
    plt.close()

def collect_plots(output):
    os.makedirs(output, exist_ok=True)
    for ss_ratio in ss_ratios:
        save_path = f"{output}/ss_{ss_ratio}.png"
        plot_largest_vs_time(ss_ratio, save_path)
        print(f"Saved {save_path}")




'''for ss_ratio in ss_ratios:
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
                    flush=True)'''
collect_plots('figure_2a_temps')
