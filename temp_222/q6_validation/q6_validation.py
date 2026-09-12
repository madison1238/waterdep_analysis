from ovito.io import import_file
from q6_functions import *
from plots import *
from pyscal_methods import *
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier,
    VoronoiAnalysisModifier
)
import config
import numpy as np
import csv
import os
import freud
from ovito_utils import *




pipeline = import_file(config.dump)
print("Frames:", pipeline.source.num_frames, flush=True)

pipeline.modifiers.append(ChillPlusModifier())
pipeline.modifiers.append(ExpressionSelectionModifier(expression="StructureType == 1 || StructureType == 2"))
pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,only_selected=True,sort_by_size=True))
pipeline.modifiers.append(VoronoiAnalysisModifier())


os.makedirs(config.output, exist_ok=True)
output_file = f"{config.output}/ice_clusters.csv"


with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "frame",
        "timestep",
        "largest_cluster",
        "q6",
        "q4",
        "ih",
        "ic",
        "ice_like",
        "num_clusters",
        "mean_cn",
        "std_cn",
    ])

    for frame in range(pipeline.source.num_frames):
        data = pipeline.compute(frame)
        coordination = np.sum(np.asarray(data.particles["Voronoi Index"]),axis=1)
        structure_types = np.asarray(data.particles["Structure Type"])
        ih = np.sum(structure_types == 1)
        ic = np.sum(structure_types == 2)
        ice_like = ih + ic

        num_clusters = int(data.attributes.get("ClusterAnalysis.cluster_count",0))
        largest_cluster = int(data.attributes.get("ClusterAnalysis.largest_size",0))
        timestep = int(data.attributes["Timestep"])

        ids = np.asarray(data.particles["Particle Identifier"])
        positions = np.asarray(data.particles["Position"])
        cluster_ids = np.asarray(data.particles["Cluster"])

        cell = data.cell
        box = freud.box.Box(
            Lx=cell[0, 0],
            Ly=cell[1, 1],
            Lz=cell[2, 2]
        )

        q6 = pyscal_steinhardt(positions,box, method='cutoff',averaged=True,cutoff=3.5,param=6)
        q4 = pyscal_steinhardt(positions,box, method='cutoff',averaged=True,cutoff=3.5,param=4)

        unique_clusters = np.unique(cluster_ids)
        largest_cluster_id = None
        largest_size = 0
        for cluster_id in unique_clusters:
            if cluster_id == 0:
                continue
            cluster_indices = np.where(cluster_ids == cluster_id)[0]
            cluster_size = len(cluster_indices)
            if cluster_size > largest_size:
                largest_size = cluster_size
                largest_cluster_id = cluster_id

        if largest_cluster_id is not None:
            largest_indices = np.where(cluster_ids == largest_cluster_id)[0]
            largest_particles = ids[largest_indices]

            cluster_cn = coordination[largest_indices]
            mean_cn = np.mean(cluster_cn)
            std_cn = np.std(cluster_cn)

            cluster_q6 = calculate_cluster_steinhardt(largest_particles,ids,q6)
            cluster_q4 = calculate_cluster_steinhardt(largest_particles,ids,q4)
        else:
            cluster_q6 = np.nan
            cluster_q4 = np.nan
            mean_cn = np.nan
            std_cn = np.nan
        
        writer.writerow([
            frame,
            timestep,
            largest_cluster,
            cluster_q6,
            cluster_q4,
            ih,
            ic,
            ice_like,
            num_clusters,
            mean_cn,
            std_cn,
        ])

        print(
            f"Frame {frame:3d} | "
            f"Timestep {timestep:8d} | "
            f"Ih {ih:4d} | "
            f"Ic {ic:4d} | "
            f"Ice {ice_like:4d} | "
            f"Clusters {num_clusters:4d} | "
            f"Largest {largest_cluster:4d} | "
            f"Q6 {cluster_q6:.4f} | "
            f"Q4 {cluster_q4:.4f}",
            flush=True
        )







