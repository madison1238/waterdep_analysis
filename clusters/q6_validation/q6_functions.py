import numpy as np
from collections import defaultdict

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
            if line.strip() != "ITEM: TIMESTEP":
                continue

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
            break
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

            if line.strip() != "ITEM: TIMESTEP":
                continue

            timestep = int(f.readline().strip())
            if timestep != target_timestep: continue
            f.readline()
            num_atoms = int(f.readline().strip())

            f.readline()
            f.readline()
            f.readline()
            f.readline()

            for i in range(num_atoms):
                parts = f.readline().split()

                particle_id = int(parts[0])
                cluster_id = int(float(parts[5]))

                clusters[cluster_id].add(particle_id)

            break

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
