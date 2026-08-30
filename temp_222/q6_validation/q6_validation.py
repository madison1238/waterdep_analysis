from ovito.io import import_file
from plots import *
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier
)
import config
import numpy as np
import csv
import os




pipeline = import_file(config.dump)
print("Frames:", pipeline.source.num_frames, flush=True)

pipeline.modifiers.append(ChillPlusModifier())
pipeline.modifiers.append(ExpressionSelectionModifier(expression="StructureType == 1 || StructureType == 2"))
pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,only_selected=True,sort_by_size=True))

os.makedirs(config.output, exist_ok=True)
output_file = f"{config.output}/ice_clusters.csv"


with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "frame",
        "timestep",
        "ih",
        "ic",
        "ice_like",
        "num_clusters",
        "largest_cluster"
    ])

    for frame in range(pipeline.source.num_frames):
        data = pipeline.compute(frame)
        structure_types = np.asarray(data.particles["Structure Type"])
        ih = np.sum(structure_types == 1)
        ic = np.sum(structure_types == 2)
        ice_like = ih + ic

        num_clusters = int(data.attributes.get("ClusterAnalysis.cluster_count",0))
        largest_cluster = int(data.attributes.get("ClusterAnalysis.largest_size",0))
        timestep = int(data.attributes["Timestep"])

        writer.writerow([
            frame,
            timestep,
            ih,
            ic,
            ice_like,
            num_clusters,
            largest_cluster
        ])

        print(
            f"Frame {frame:3d} | "
            f"Timestep {timestep:8d} | "
            f"Ih {ih:4d} | "
            f"Ic {ic:4d} | "
            f"Ice {ice_like:4d} | "
            f"Clusters {num_clusters:4d} | "
            f"Largest {largest_cluster:4d}",
            flush=True
        )

plot_largest_vs_time(f"{config.output}/ice_clusters.csv", f"{config.output}/largest_vs_time.png")







