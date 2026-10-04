
dump_file = "./dump.cluster.lammpstrj"
target = 1000000
info_file = "clusters.txt"
clusters = {}

with open(info_file, 'w')as f:
    f.write("CLUSTER INFO\n\n")

with open (dump_file, 'r') as f:
    found_timestep = False
    num_atoms = 0
    while True:
        line = f.readline()

        if not line:
            break
        if line.strip() == "ITEM: TIMESTEP":
            timestep = int(f.readline().strip())

            if timestep == target:
                found_timestep = True

                f.readline()
                num_atoms = int(f.readline().strip())

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                for i in range(num_atoms):
                    atoms_line = f.readline().split()
                    atom_id = int(atoms_line[0])
                    cluster_id = int(atoms_line[5])

                    if cluster_id not in clusters:
                        clusters[cluster_id] = 1
                    else:
                        clusters[cluster_id] += 1
                break
if not found_timestep:
    with open(info_file, 'a') as f:
        f.write(f"Timestep {target} not found")
else:

    sorted_clusters = sorted(
    clusters.items(),
    key=lambda x: x[1],
    reverse=True
    )

    vapor_atoms = 0
    condensed_atoms = 0
    for cluster_id, size in sorted_clusters:
        if size < 4:
            vapor_atoms += size
        else:
            condensed_atoms += size

    box_length = 650.0
    box_volume = box_length ** 3
    vapor_density = vapor_atoms / box_volume

    with open(info_file, 'a') as f:
        f.write(f"Total number of clusters: {len(clusters)}\n")
        f.write(f"Largest cluster size: {sorted_clusters[0][1]} atoms\n")
        f.write(f"Vapor atoms (size < 4): {vapor_atoms} atoms\n")
        f.write(f"Condensed Atoms: {condensed_atoms} atoms\n")
        f.write(f"Vapor density: {vapor_density:.8e}\n")
        f.write(f"Cluster sizes at timestep {target}:\n")
        for cluster_id, size in sorted_clusters:
            f.write(f"Cluster {cluster_id}: {size} atoms\n")
    

    


        


