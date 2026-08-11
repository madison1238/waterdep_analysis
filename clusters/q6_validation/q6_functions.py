import numpy as np
from collections import defaultdict
from pyscal_methods import *
from ovito_utils import * 
import csv

def find_last_timestep(filename):
    final_frame = -1
    final_timestep = None
    with open(filename, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
                final_timestep = timestep
                final_frame += 1
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                for i in range(num_atoms):
                    line = f.readline()
    return final_timestep, final_frame
                
                

def find_largest_clusters(filename, final_timestep):
    clusters = defaultdict(list)

    with open(filename, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":

                timestep = int(f.readline().strip())
                if timestep != final_timestep: continue
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                for i in range(num_atoms):
                    line = f.readline()
                    parts = line.split()
                    particle_id = int(float(parts[0]))
                    cluster_id = int(float(parts[5]))
                    clusters[cluster_id].append(particle_id)
    top4 = sorted(
        clusters.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:4]

    final_clusters = {}
    for cluster_id, particle_ids in top4:
        final_clusters[cluster_id] = {
            "size": len(particle_ids),
            "particle_ids": set(particle_ids)
        }

    return final_clusters 

def get_clusters_at_timestep(filename, target_timestep):
    clusters = defaultdict(set)

    with open(filename, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break

            if line.strip() == "ITEM: TIMESTEP":

                timestep = int(f.readline().strip())
                if timestep != target_timestep: continue
                f.readline()
                num_atoms = int(f.readline().strip())

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                for i in range(num_atoms):
                    parts = f.readline().split()

                    particle_id = int(float(parts[0]))
                    cluster_id = int(float(parts[5]))

                    clusters[cluster_id].add(particle_id)
    return clusters



def find_best_cluster_match(tracked_particles, clusters):
    best_cluster_id = None
    best_overlap = 0
    best_score = 0

    tracked_size = len(tracked_particles)
    if tracked_size == 0:
        return None, 0, 0.0

    for cluster_id, particle_ids in clusters.items():
        overlap = len(tracked_particles & particle_ids)
        score = overlap /tracked_size
        if score > best_score:
            best_score = score
            best_overlap = overlap
            best_cluster_id = cluster_id
    return best_cluster_id, best_overlap, best_score

def calculate_cluster_q6(tracked_particles, ids, positions, box):
    q6 = pyscal_steinhardt(positions,box, method='cutoff',averaged=True,cutoff=3.5,param=6)
    id_to_index = {particle_id: i for i, particle_id in enumerate(ids)}
    tracked_indices = [id_to_index[particle_id]for particle_id in tracked_particles if particle_id in id_to_index]

    cluster_q6 = q6[tracked_indices]
    average_q6 = np.mean(cluster_q6)
    return average_q6

def get_dominant_phase_per_cluster(cluster_ids, labels):
    cluster_ids = np.asarray(cluster_ids)
    labels = np.asarray(labels)

    unique_clusters, inverse = np.unique(cluster_ids, return_inverse=True)
    phase_counts = np.zeros((len(unique_clusters), 6),dtype=np.int32)
    np.add.at(phase_counts,(inverse, labels),1)
    dominant_phase_indices = np.argmax(phase_counts,axis=1)
    phase_names = np.array(["liquid","ice_ih", "ice_ic","interfacial","hydrate","interfacial_hydrate"])
    dominant_phases = phase_names[dominant_phase_indices]
    cluster_phases = dict(zip(unique_clusters, dominant_phases))
    return cluster_phases



def track_cluster_q6(filename, final_timestep, final_frame, final_cluster_id, 
                     final_cluster_particles, final_cluster_size, final_cluster_rank,
                     interval, output_csv):
    print(f"Starting tracking for cluster {final_cluster_id}",flush=True)
    
    fieldnames = [
        "final_cluster_rank",
        "final_cluster_id",
        "final_cluster_size",
        "timestep",
        "time_ns",
        "cluster_id",
        "cluster_size",
        "overlap",
        "overlap_score",
        "avg_q6"
    ]

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        f.flush()

        tracked_particles = set(final_cluster_particles)
        current_timestep = final_timestep
        current_frame = final_frame

        while current_timestep >= 0:
            

            if current_timestep == final_timestep:
                cluster_id = final_cluster_id
                cluster_size = len(tracked_particles)
                overlap = np.nan
                overlap_score = np.nan
            else:
                clusters = get_clusters_at_timestep(filename,current_timestep)
                match_id, overlap, overlap_score = (find_best_cluster_match(tracked_particles,clusters))
                if match_id is None:
                    print(f"No reliable match found at timestep: {current_timestep}")
                    break
                tracked_particles = clusters[match_id]
                cluster_id = match_id
                cluster_size = len(tracked_particles)

            ids, positions, box = load_frame(filename, frame=current_frame)
            average_q6 = calculate_cluster_q6(tracked_particles,ids,positions,box)
            time_ns = current_timestep * 5e-6

            writer.writerow({
                "final_cluster_rank": final_cluster_rank,
                "final_cluster_id": final_cluster_id,
                "final_cluster_size": final_cluster_size,
                "timestep": current_timestep,
                "time_ns": time_ns,
                "cluster_id": cluster_id,
                "cluster_size": cluster_size,
                "overlap": overlap,
                "overlap_score": overlap_score,
                "avg_q6": average_q6
            })
            f.flush()

            print(
                f"Timestep: {current_timestep}, "
                f"Cluster: {cluster_id}, "
                f"Size: {cluster_size}, "
                f"Overlap: {overlap}, "
                f"Score: {overlap_score}, "
                f"Q6: {average_q6:.4f}",
                flush=True
            )

            current_timestep -= interval
            current_frame -= 1
