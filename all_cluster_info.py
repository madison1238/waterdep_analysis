import matplotlib.pyplot as plt

all_vapor_density = []
all_timesteps = []
dump_file = "./dump.cluster.lammpstrj"
info_file = "clusters.txt"
box_length = 650.0
box_volume = box_length ** 3

with open(info_file, 'w')as f:
    f.write("CLUSTER INFO\n\n")

with open (dump_file, 'r') as dump:
    while True:
        line = dump.readline()
        if not line:
            break
        if line.strip() == "ITEM: TIMESTEP":
            timestep = int(dump.readline().strip())

            dump.readline()
            num_atoms = int(dump.readline().strip())

            dump.readline()
            dump.readline()
            dump.readline()
            dump.readline()
            dump.readline()

            clusters = {}

            for i in range(num_atoms):
                atoms_line = dump.readline().split()
                cluster_id = int(atoms_line[5])

                if cluster_id not in clusters:
                    clusters[cluster_id] = 1
                else:
                    clusters[cluster_id] += 1

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

            
            vapor_density = vapor_atoms / box_volume

            all_timesteps.append(timestep)
            all_vapor_density.append(vapor_density)

            with open(info_file, 'a') as f:
                f.write(f"CLUSTER INFO AT TIMESTEP {timestep}:\n\n")
                f.write(f"Total number of clusters: {len(clusters)}\n")
                f.write(f"Largest cluster size: {sorted_clusters[0][1]} atoms\n")
                f.write(f"Vapor atoms (size < 4): {vapor_atoms} atoms\n")
                f.write(f"Condensed Atoms: {condensed_atoms} atoms\n")
                f.write(f"Vapor density: {vapor_density:.8e}\n")
                f.write(f"Cluster sizes at timestep {timestep}:\n\n")
                for cluster_id, size in sorted_clusters:
                    f.write(f"Cluster {cluster_id}: {size} atoms\n")
                


plt.figure()
plt.plot(all_timesteps,all_vapor_density, marker="o")
plt.title("Vapor Density vs Timesteps")
plt.xlabel("Timestep")
plt.ylabel("Vapor Density")
plt.savefig("timestep_vs_density.png")