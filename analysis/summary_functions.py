import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from scipy.spatial import cKDTree
import os
import csv


def plot_largest(x_val, y_val):
    femtoseconds = [x * 5 for x in x_val]
    plt.figure()
    plt.plot(femtoseconds, y_val)
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Largest Cluster Size")
    plt.title("Largest Cluster Size vs Time")
    plt.tight_layout()
    plt.savefig('../summary/largest_vs_time.png')
    plt.close()

def plot_average_size(x_val, y_val):
    femtoseconds = [x * 5 for x in x_val]
    plt.figure()
    plt.plot(femtoseconds, y_val)
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Average Cluster Size")
    plt.title("Average Cluster Size vs Time")
    plt.tight_layout()
    plt.savefig('../summary/average_vs_time.png')
    plt.close()

def plot_cluster_dist_hist(distributions, selected_timesteps):
    fig, axes = plt.subplots(2,2, figsize=(10,8))

    all_sizes = []
    max_frequency = 0

    for timestep in selected_timesteps:
        filtered_sizes = [s for s in distributions[timestep] if s>2]
        all_sizes.extend(filtered_sizes)

        if filtered_sizes:
            counts,_ = np.histogram(filtered_sizes,bins=20)
            max_frequency = max(max_frequency, counts.max())
    if all_sizes:
        max_cluster_size = max(all_sizes)
    else:
        max_cluster_size = 1

    for ax, timestep in zip(axes.flat, selected_timesteps):
        filtered_sizes = [s for s in distributions[timestep] if s>2]
        if filtered_sizes:
            bins = np.linspace(0,max_cluster_size,21)
            ax.hist(filtered_sizes, bins=bins)
        else:
            ax.text(
                0.5, 0.5,
                'No clusters > 2',
                ha='center',
                va='center'
            )

        ax.set_xlim(0,max_cluster_size)
        ax.set_ylim(0, max_frequency)

        ax.set_title(f"{timestep * 5:.0f} fs")
        ax.set_xlabel('Cluster Size')
        ax.set_ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('../summary/cluster_size_distribution_hist.png')
    plt.close()

def plot_cluster_dist_loglog(distributions, selected_timesteps):
    fig, axes = plt.subplots(2,2, figsize=(10,8))

    all_sizes = []
    all_counts = []

    for timestep in selected_timesteps:
        sizes = [s for s in distributions[timestep] if s > 2]

        counts = Counter(sizes)

        all_sizes.extend(counts.keys())
        all_counts.extend(counts.values())
    xmin = min(all_sizes)
    xmax = max(all_sizes)

    ymin = min(all_counts)
    ymax = max(all_counts)

    for ax, timestep in zip(axes.flat, selected_timesteps):
        filtered_sizes = [s for s in distributions[timestep] if s>2]
        if filtered_sizes:

            counts = Counter(filtered_sizes)
            x = sorted(counts.keys())
            y = [counts[size] for size in x]

            ax.loglog(x,y,'o')
        else:
            ax.text(
                0.5, 0.5,
                'No clusters > 2',
                ha='center',
                va='center'
            )
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_title(f"{timestep * 5:.0f} fs")
        ax.set_xlabel('Cluster Size')
        ax.set_ylabel('Frequency')

    plt.tight_layout()
    plt.savefig('../summary/cluster_size_distribution_loglog.png')
    plt.close()
        
#new analyze function attempts weighted q6 calc with neighbors
def analyze_cluster_weighted(filename):
    timesteps = []
    largest_clusters = []
    largest_cluster_ids = []
    largest_cluster_q6s = []
    average_clusters = []
    csv_rows = []
    output_file_cluster = '../summary/cluster_summary.txt'
    output_file_q6 = '../summary/q6_summary.txt'
    final_cluster_sizes = {}
    cluster_distrbution = {}
    average_clusters_q6 = {}


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
                cluster_q6 = {}
                cluster_avg_q6 = {}

                for i in range(num_atoms):
                    atoms_line = f.readline().split()

                    cluster_id = int(float(atoms_line[5]))
                    q6 = float(atoms_line[6])

                    if cluster_id in cluster_sizes:
                        cluster_sizes[cluster_id] += 1
                    else:
                        cluster_sizes[cluster_id] = 1
                    
                    if cluster_id in cluster_q6:
                        cluster_q6[cluster_id].append(q6)
                    else:
                        cluster_q6[cluster_id] = [q6]
                sizes = list(cluster_sizes.values())
                cluster_q6_stats = {}

                for cluster_id, q6_values in cluster_q6.items():

                    avg_q6 = sum(q6_values) / len(q6_values)

                    cluster_q6_stats[cluster_id] = {
                        "avg": avg_q6,
                        "min": min(q6_values),
                        "max": max(q6_values)
                    }

                    cluster_avg_q6[cluster_id] = avg_q6
                
                
                weighted_q6_sum = 0
                total_cluster_atoms = 0

                for cluster_id, avg_q6 in cluster_avg_q6.items():
                    cluster_size = cluster_sizes[cluster_id]

                    if cluster_size > 2:
                        weighted_q6_sum += avg_q6 * cluster_size 
                        total_cluster_atoms += cluster_size

                if total_cluster_atoms > 0:
                    average_clusters_q6[timestep] = weighted_q6_sum / total_cluster_atoms
                else:
                    average_clusters_q6[timestep] = 0


                if len(sizes) == 0:
                    largest_cluster = -1
                    average_cluster = -1
                    largest_cluster_id = -1
                    largest_cluster_q6 = 0
                else:
                    largest_cluster_id = max(cluster_sizes, key=cluster_sizes.get)

                    largest_cluster = cluster_sizes[largest_cluster_id]

                    largest_cluster_q6 = cluster_avg_q6.get(largest_cluster_id,0)

                    filtered_sizes = [s for s in sizes if s>2]

                    if len(filtered_sizes) > 0:
                        average_cluster = sum(filtered_sizes) / len(filtered_sizes)
                    else:
                        average_cluster = 0
                
                final_cluster_sizes = cluster_sizes.copy()
                final_timestep = timestep
                
                largest_cluster_q6s.append(largest_cluster_q6)
                timesteps.append(timestep)
                largest_clusters.append(largest_cluster)
                largest_cluster_ids.append(largest_cluster_id)
                average_clusters.append(average_cluster)

                csv_rows.append([timestep,
                                largest_cluster_id,
                                largest_cluster,
                                round(average_cluster, 3)])

                with open(output_file_cluster, 'a') as output:
                    output.write(f"Timestep: {timestep}\n")
                    output.write(f"Lagrgest Cluster ID: {largest_cluster_id}\n")
                    output.write(f"Largest Cluster Size: {largest_cluster}\n")
                    output.write(f"Average Cluster Size (>2): {average_cluster:.2f}\n")
                    output.write(f"{'=' * 20}\n\n")


                with open(output_file_q6, 'a' ) as out:
                    out.write('=' * 50 + "\n")
                    out.write(f"Timestep: {timestep}\n")
                    out.write('=' * 50 + "\n\n")

                    for cluster_id in sorted(cluster_q6_stats):

                        cluster_size = cluster_sizes[cluster_id]

                        if cluster_size <= 2:
                            continue

                        stats = cluster_q6_stats[cluster_id]

                        out.write(f"Cluster ID: {cluster_id}\n")
                        out.write(f"Cluster Size: {cluster_size}\n")
                        out.write(f"Average Q6: {stats['avg']:.3f}\n")
                        out.write(f"Minimum Q6: {stats['min']:.3f}\n")
                        out.write(f"Maximum Q6: {stats['max']:.3f}\n")
                        out.write('-' * 40 + '\n')

                
                cluster_distrbution[timestep] = sizes

    results = {
        "timesteps": timesteps,
        "largest_clusters": largest_clusters,
        "largest_cluster_ids": largest_cluster_ids,
        "average_clusters": average_clusters,
        "cluster_distribution": cluster_distrbution,
        'final_cluster_sizes': final_cluster_sizes,
        'average_clusters_q6': average_clusters_q6,
        "csv_rows": csv_rows,
        'largest_cluster_q6s': largest_cluster_q6s
    }
    return results






#og analyze function
def analyze_clusters(filename):
    timesteps = []
    largest_clusters = []
    largest_cluster_ids = []
    largest_cluster_q6s = []
    average_clusters = []
    csv_rows = []
    output_file_cluster = '../summary/cluster_summary.txt'
    output_file_q6 = '../summary/q6_summary.txt'
    final_cluster_sizes = {}
    cluster_distrbution = {}
    average_clusters_q6 = {}


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
                cluster_q6 = {}
                cluster_avg_q6 = {}

                for i in range(num_atoms):
                    atoms_line = f.readline().split()

                    cluster_id = int(float(atoms_line[5]))
                    q6 = float(atoms_line[6])

                    if cluster_id in cluster_sizes:
                        cluster_sizes[cluster_id] += 1
                    else:
                        cluster_sizes[cluster_id] = 1
                    
                    if cluster_id in cluster_q6:
                        cluster_q6[cluster_id].append(q6)
                    else:
                        cluster_q6[cluster_id] = [q6]
                sizes = list(cluster_sizes.values())
                cluster_q6_stats = {}

                for cluster_id, q6_values in cluster_q6.items():

                    avg_q6 = sum(q6_values) / len(q6_values)

                    cluster_q6_stats[cluster_id] = {
                        "avg": avg_q6,
                        "min": min(q6_values),
                        "max": max(q6_values)
                    }

                    cluster_avg_q6[cluster_id] = avg_q6
                
                
                weighted_q6_sum = 0
                total_cluster_atoms = 0

                for cluster_id, avg_q6 in cluster_avg_q6.items():
                    cluster_size = cluster_sizes[cluster_id]

                    if cluster_size > 2:
                        weighted_q6_sum += avg_q6 * cluster_size 
                        total_cluster_atoms += cluster_size

                if total_cluster_atoms > 0:
                    average_clusters_q6[timestep] = weighted_q6_sum / total_cluster_atoms
                else:
                    average_clusters_q6[timestep] = 0


                if len(sizes) == 0:
                    largest_cluster = -1
                    average_cluster = -1
                    largest_cluster_id = -1
                    largest_cluster_q6 = 0
                else:
                    largest_cluster_id = max(cluster_sizes, key=cluster_sizes.get)

                    largest_cluster = cluster_sizes[largest_cluster_id]

                    largest_cluster_q6 = cluster_avg_q6.get(largest_cluster_id,0)

                    filtered_sizes = [s for s in sizes if s>2]

                    if len(filtered_sizes) > 0:
                        average_cluster = sum(filtered_sizes) / len(filtered_sizes)
                    else:
                        average_cluster = 0
                
                final_cluster_sizes = cluster_sizes.copy()
                final_timestep = timestep
                
                largest_cluster_q6s.append(largest_cluster_q6)
                timesteps.append(timestep)
                largest_clusters.append(largest_cluster)
                largest_cluster_ids.append(largest_cluster_id)
                average_clusters.append(average_cluster)

                csv_rows.append([timestep,
                                largest_cluster_id,
                                largest_cluster,
                                round(average_cluster, 3)])

                with open(output_file_cluster, 'a') as output:
                    output.write(f"Timestep: {timestep}\n")
                    output.write(f"Lagrgest Cluster ID: {largest_cluster_id}\n")
                    output.write(f"Largest Cluster Size: {largest_cluster}\n")
                    output.write(f"Average Cluster Size (>2): {average_cluster:.2f}\n")
                    output.write(f"{'=' * 20}\n\n")


                with open(output_file_q6, 'a' ) as out:
                    out.write('=' * 50 + "\n")
                    out.write(f"Timestep: {timestep}\n")
                    out.write('=' * 50 + "\n\n")

                    for cluster_id in sorted(cluster_q6_stats):

                        cluster_size = cluster_sizes[cluster_id]

                        if cluster_size <= 2:
                            continue

                        stats = cluster_q6_stats[cluster_id]

                        out.write(f"Cluster ID: {cluster_id}\n")
                        out.write(f"Cluster Size: {cluster_size}\n")
                        out.write(f"Average Q6: {stats['avg']:.3f}\n")
                        out.write(f"Minimum Q6: {stats['min']:.3f}\n")
                        out.write(f"Maximum Q6: {stats['max']:.3f}\n")
                        out.write('-' * 40 + '\n')

                
                cluster_distrbution[timestep] = sizes

    results = {
        "timesteps": timesteps,
        "largest_clusters": largest_clusters,
        "largest_cluster_ids": largest_cluster_ids,
        "average_clusters": average_clusters,
        "cluster_distribution": cluster_distrbution,
        'final_cluster_sizes': final_cluster_sizes,
        'average_clusters_q6': average_clusters_q6,
        "csv_rows": csv_rows,
        'largest_cluster_q6s': largest_cluster_q6s
    }
    return results



#FUNCTIONS FOR Q6 INFO  

def plot_average_q6_vs_timestep(q6_by_timestep, title):
    femtoseconds = []
    average_q6s = []
    for timestep in sorted(q6_by_timestep):
        femtoseconds.append(timestep * 5)
        average_q6s.append(q6_by_timestep[timestep])
    plt.plot(femtoseconds, average_q6s, marker='o')
    plt.xlabel("Time (fs)")
    plt.ylabel("Average q6")
    plt.title("Average Cluster q6 vs Time")
    plt.tight_layout()
    plt.savefig(title)
    plt.close()
        
def plot_largest_cluster_q6_change(timesteps, largest_cluster_q6s, title):
    femtoseconds = [t * 5 for t in timesteps]
    plt.plot(
        femtoseconds,
        largest_cluster_q6s,
        marker='o'
    )

    plt.xlabel("Time (fs)")
    plt.ylabel("Average q6")
    plt.title("Largest Cluster q6 vs Time")
    plt.tight_layout()
    plt.savefig(title)
    plt.close()

def get_selected_q6_dist(selected_timesteps, filename):
    selected_q6_dist = {}
    
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

                cluster_q6 = {}

                for i in range(num_atoms):
                    atoms_line = f.readline().split()

                    cluster_id = int(float(atoms_line[5]))
                    q6 = float(atoms_line[6])

                    if cluster_id in cluster_q6:
                        cluster_q6[cluster_id].append(q6)
                    else:
                        cluster_q6[cluster_id] = [q6]

                if timestep not in selected_timesteps:
                    continue

                q6_distributions = []

                for cluster_id, q6_values in cluster_q6.items():
                    cluster_size = len(q6_values)

                    if cluster_size <= 2:
                        continue

                    avg_q6 = sum(q6_values) / cluster_size
                    q6_distributions.append(avg_q6)
                selected_q6_dist[timestep] = q6_distributions
    return selected_q6_dist



def plot_q6_dist_hist(distributions, selected_timesteps):
    fig, axes = plt.subplots(2,2, figsize=(10,8))

    all_q6 = []
    max_frequency = 0

    for timestep in selected_timesteps:
        q6_values = distributions[timestep]
        all_q6.extend(q6_values)

        if q6_values:
            counts, _ = np.histogram(q6_values, bins=20)
            max_frequency = max(max_frequency, counts.max())

    if all_q6:
        min_q6 = min(all_q6)
        max_q6 = max(all_q6)
    else:
        min_q6 = 0
        max_q6 = 1

    bins = np.linspace(min_q6, max_q6, 21)

    for ax, timestep in zip(axes.flat, selected_timesteps):
        q6_values = distributions[timestep]
        if q6_values:
            ax.hist(q6_values, bins=bins)
        else:
            ax.text(
                0.5, 0.5,
                'No clusters > 2',
                ha='center',
                va='center'
            )

        ax.set_xlim(0,max_q6)
        ax.set_ylim(0, max_frequency)

        ax.set_title(f"{timestep * 5:.0f} fs")
        ax.set_xlabel('Cluster Q6')
        ax.set_ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('../summary/cluster_q6_distribution_hist.png')
    plt.close()





# FUNCTIONS TO TRACK CLUSTER THROUGH SIMULATION
def track_cluster_growth(filename, target_cluster_id):
    timesteps = []
    final_clusters = {}
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

                cluster_members = {}
                for i in range(num_atoms):
                    atoms_line = f.readline().split()
                    cluster_id = int(float(atoms_line[5]))
                    atom_id = int(float(atoms_line[0]))

                    if cluster_id not in cluster_members:
                        cluster_members[cluster_id] = set()
                    cluster_members[cluster_id].add(atom_id)
                timesteps.append(timestep)
                final_clusters = cluster_members.copy()
    target_atoms = final_clusters[target_cluster_id]
    history_timesteps = []
    history_sizes = []

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

                cluster_members = {}
                for i in range(num_atoms):
                    atoms_line = f.readline().split()
                    cluster_id = int(float(atoms_line[5]))
                    atom_id = int(float(atoms_line[0]))
                    if cluster_id not in cluster_members:
                        cluster_members[cluster_id] = set()
                    cluster_members[cluster_id].add(atom_id)
                best_cluster = None
                best_overlap = 0

                for cluster_id, members in cluster_members.items():
                    overlap = len(members & target_atoms)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_cluster = cluster_id
                history_timesteps.append(timestep)
                if best_cluster is not None:
                    history_sizes.append(
                        len(cluster_members[best_cluster])
                    )
                else:
                    history_sizes.append(0)
    return(history_sizes, history_timesteps)



def plot_cluster_growth(timesteps, sizes, output_file,ranking):
    femtoseconds = [t*5 for t in timesteps]
    plt.figure()
    plt.plot(femtoseconds, sizes)
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Cluster Size")
    if ranking == 1:
        plt.title("Growth of Largest Cluster")
    elif ranking == 2:
        plt.title("Growth of Second Largest Cluster")
    elif ranking == 3:
        plt.title("Growth of Third Largest Cluster")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
