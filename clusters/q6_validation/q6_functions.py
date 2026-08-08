import numpy as np

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
                
                

def find_largest_clusters(filename):
    cluster_sizes = {}
    with open(filename, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                cluster_sizes = {}

                for i in range(num_atoms):
                    line = f.readline()
                    cluster_id = int(float(line.split()[5]))
                    cluster_sizes[cluster_id] = (cluster_sizes.get(cluster_id, 0) + 1)
    top4 = sorted(
        cluster_sizes.items(),
        key=lambda x: x[1],
        reverse=True
    )[:4]

    return top4 



def get_cluster_members(filename):
    cluster_members = {}

    with open(filename, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break

            if line.strip() == "ITEM: TIMESTEP":

                timestep = int(f.readline().strip())

                f.readline()
                num_atoms = int(float(f.readline().strip()))

                for _ in range(5):
                    f.readline()

                cluster_members = {}

                for _ in range(num_atoms):

                    line = f.readline().split()

                    cid = int(float(line[5]))
                    atom_id = int(float(line[0]))

                    if cid not in cluster_members:
                        cluster_members[cid] = set()

                    cluster_members[cid].add(atom_id)

    return cluster_members


def find_matching_cluster(target_atoms, cluster_members, min_overlap=1):
    best_cluster = None
    best_overlap = 0

    for cluster_id, members in cluster_members.items():

        overlap = len(target_atoms & members)

        if overlap > best_overlap:
            best_overlap = overlap
            best_cluster = cluster_id

    if best_overlap < min_overlap:
        return None, best_overlap

    return best_cluster, best_overlap




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
