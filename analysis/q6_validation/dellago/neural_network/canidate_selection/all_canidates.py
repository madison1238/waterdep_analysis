import os
import csv

sims = 300
min_cluster_size = 10
max_cluster_size = 60
total = 0
candidate_file = "all_candidates.csv"

with open(candidate_file, "w", newline="") as outfile:
    writer = None
    for sim_num in range(sims):
        dump_file = f"../../sims/sim_{sim_num}/dump.mWC2.lammpstrj"
        ice_file = f"../../sims/sim_{sim_num}/summary/ice_clusters.csv"
        if not os.path.exists(ice_file):
            print(f"Warning: Missing file: {ice_file}")
            continue
        with open(ice_file, "r", newline="") as infile:
            reader = csv.DictReader(infile)
            if writer is None:
                fieldnames = ['Dump Path', 'Frame', 'Timestep', 'Largest Cluster Size (n)', 'Size Bin' ]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

            for row in reader:
                try:
                    cluster_size = int(float(row["largest_cluster"]))
                except (ValueError, KeyError):
                    continue
                if min_cluster_size <= cluster_size <= max_cluster_size:
                    if cluster_size < 20:
                        size_bin = "10-19"
                    elif cluster_size < 30:
                        size_bin = "20-29"
                    elif cluster_size < 40:
                        size_bin = "30-39"
                    elif cluster_size < 50:
                        size_bin = "40-49"
                    else:
                        size_bin = "50-60"
                    frame = int(row["frame"])
                    timestep = int(row["timestep"])


                    writer.writerow({
                        "Dump Path": dump_file,
                        "Frame": frame,
                        "Timestep": timestep,
                        "Largest Cluster Size (n)": cluster_size,
                        "Size Bin": size_bin
                    })

                    total += 1

print(f"Total eligible candidate frames: {total}")