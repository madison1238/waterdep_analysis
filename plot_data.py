import matplotlib.pyplot as plt
import os
import csv

os.makedirs( 'summary',exist_ok=True)


output_file = 'summary/cluster_summary.txt'
ten_largest_file = 'summary/largest_ten_cluster.txt'

timesteps = []
largest_clusters = []
largest_cluster_ids = []
average_clusters = []
csv_rows = []
final_timestep = None
final_cluster_sizes = {}
cluster_distrbution = {}

def plot_largest(x_val, y_val):
    femtoseconds = [x * 5 for x in x_val]
    plt.figure()
    plt.plot(femtoseconds, y_val)
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Largest Cluster Size")
    plt.title("Largest Cluster Size vs Time")
    plt.savefig('summary/largest_vs_time.png')
    plt.close()

def plot_average_size(x_val, y_val):
    femtoseconds = [x * 5 for x in x_val]
    plt.figure()
    plt.plot(femtoseconds, y_val)
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Average Cluster Size")
    plt.title("Average Cluster Size vs Time")
    plt.savefig('summary/average_vs_time.png')
    plt.close()

def plot_cluster_dist(distributions, selected_timesteps):
    fig, axes = plt.subplots(2,2, figsize=(10,8))

    for ax, timestep in zip(axes.flat, selected_timesteps):
        filtered_sizes = [s for s in distributions[timestep] if s>2]
        if filtered_sizes:
            ax.hist(filtered_sizes, bins=20)
        else:
            ax.text(
                0.5, 0.5,
                'No clusters > 2',
                ha='center',
                va='center'
            )
        ax.set_title(f"{timestep * 5:.0f} fs")
        ax.set_xlabel('Cluster Size')
        ax.set_ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('summary/cluster_size_distribution.png')
    plt.close()





with open(output_file, 'w') as f:
    f.write("CLUSTER SUMMARY FILE\n")
    f.write(f"{'='*30}\n\n")
with open(ten_largest_file, 'w') as f:
    f.write('Top 10 Largest Clusters at Final Timestep\n')
    f.write(f"{'='*30}\n\n")




with open('dump.cluster.lammpstrj', 'r') as f:
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
                atoms_line = f.readline().split()
                cluster_id = int(float(atoms_line[5]))

                if cluster_id in cluster_sizes:
                    cluster_sizes[cluster_id] += 1
                else:
                    cluster_sizes[cluster_id] = 1
            sizes = list(cluster_sizes.values())

            if len(sizes) == 0:
                largest_cluster = -1
                average_cluster = -1
                largest_cluster_id = -1
            else:
                largest_cluster_id = max(cluster_sizes, key=cluster_sizes.get)

                largest_cluster = cluster_sizes[largest_cluster_id]

                filtered_sizes = [s for s in sizes if s>2]

                if len(filtered_sizes) > 0:
                    average_cluster = sum(filtered_sizes) / len(filtered_sizes)
                else:
                    average_cluster = 0
            
            final_cluster_sizes = cluster_sizes.copy()
            final_timestep = timestep
            

            timesteps.append(timestep)
            largest_clusters.append(largest_cluster)
            largest_cluster_ids.append(largest_cluster_id)
            average_clusters.append(average_cluster)

            csv_rows.append([timestep,
                             largest_cluster_id,
                             largest_cluster,
                             round(average_cluster, 3)])

            with open(output_file, 'a') as output:
                output.write(f"Timestep: {timestep}\n")
                output.write(f"Lagrgest Cluster ID: {largest_cluster_id}\n")
                output.write(f"Largest Cluster Size: {largest_cluster}\n")
                output.write(f"Average Cluster Size (>2): {average_cluster:.2f}\n")
                output.write(f"{'=' * 20}\n\n")
            
            cluster_distrbution[timestep] = sizes
            

            

plot_largest(timesteps, largest_clusters)
plot_average_size(timesteps,average_clusters)

with open('summary/cluster_summary.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow([
        'Timestep',
        'Largest Cluster ID',
        'Largest Cluster Size',
        'Average Cluster Size'
    ])

    writer.writerows(csv_rows)

all_timesteps = list(cluster_distrbution.keys())

selected_timesteps = [
    all_timesteps[len(all_timesteps) // 4],
    all_timesteps[len(all_timesteps) // 2],
    all_timesteps[(len(all_timesteps) // 4) * 3],
    all_timesteps[-1]
]

plot_cluster_dist(cluster_distrbution,selected_timesteps)



sorted_final_clusters = sorted(
    final_cluster_sizes.items(),
    key=lambda x: x[1],
    reverse=True
)


with open(ten_largest_file, 'a') as f:
    for cluster_id, size in sorted_final_clusters[:10]:
        f.write(f"Cluster {cluster_id}: {size} particles\n")


    