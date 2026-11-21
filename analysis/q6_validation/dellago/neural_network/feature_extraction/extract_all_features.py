from pathlib import Path
import csv
from functions import (largest_cluster_info,
                       largest_q6_q4_tetra,
                       largest_vol_cn,
                       calculate_i_j_k,
                       caluculate_E_1_6)

SELECTED_CONFIGS_PATH = Path("..") / "canidate_selection" / "selected_configs.csv"
INITIAL_FEATURES_PATH = Path("initial_features.csv")


with SELECTED_CONFIGS_PATH.open("r", newline="") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    candidates = list(reader)


total_configs = len(candidates)
successful = 0
failed = 0

print(f"Loaded {total_configs} configurations.", flush=True)
print("Starting feature extraction...\n", flush=True)

with INITIAL_FEATURES_PATH.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
      "config_id",
      "dump path",
      "frame",
      "timestep",
      "Largest Cluster Size (n)",
      "Size Bin",
      "Q6",
      "Q4",
      "q6",
      "q4",
      "All Tetrahedrality"
      "Tetrahedrality",
      "nih",
      "nic",
      "nih/n",
      "nic/n",
      'Coordination Number (CN)',
      "CN Standard Deviation",
      'Voronoi Volume',
      "Voronoi Volume Standard Deviation",
      "Radius of Gyration (Rg)",
      "Anisotropy (I)",
      "Acylindricity (J)",
      "Asphericity (K)",
      "E1",
      "E2",
      "E3",
      "E4",
      "E5",
      "E6"
    ])
    for index, row in enumerate(candidates, start=1):
        config_id = f"config_{index:03d}"
        row["Frame"] = int(row["Frame"])
        row["Timestep"] = int(row["Timestep"])
        row["Largest Cluster Size (n)"] = int(row["Largest Cluster Size (n)"])

        dump_path = str(row["Dump Path"])
        frame = row["Frame"]
        largest_cluster_size = row["Largest Cluster Size (n)"]
        size_bin = row["Size Bin"]

        print(f"[{index}/{total_configs}] Processing frame {frame}...", flush=True)

        try:
            timestep, largest_cluster_size, ids_in_largest, ic, ih, ic_fraction, ih_fraction,largest_cluster_radius, lambda1, lambda2, lambda3 = largest_cluster_info(dump_path,frame)
            cluster_q6, cluster_q4, cluster_tetra, local_q6, local_q4, all_tetra = largest_q6_q4_tetra(dump_path, frame, ids_in_largest)
            cluster_cn, std_cn, cluster_v_vol, std_v_vol =  largest_vol_cn(dump_path, frame, ids_in_largest)
            i,j,k = calculate_i_j_k(lambda1,lambda2,lambda3)
            E1,E2,E3,E4,E5,E6= caluculate_E_1_6(largest_cluster_size, cluster_q6,k, largest_cluster_radius, cluster_v_vol, std_v_vol, cluster_cn, std_cn )

            writer.writerow([
                config_id,
                dump_path,
                frame,
                timestep,
                largest_cluster_size,
                size_bin,
                cluster_q6,
                cluster_q4,
                local_q6,
                local_q4,
                all_tetra,
                cluster_tetra,
                ih,
                ic,
                ih_fraction,
                ic_fraction,
                cluster_cn,
                std_cn,
                cluster_v_vol,
                std_v_vol,
                largest_cluster_radius,
                i,
                j,
                k,
                E1,
                E2,
                E3,
                E4,
                E5,
                E6,
                ])
            successful += 1
            print(f"Successfully written! ({successful}/{total_configs})\n", flush=True)
        except Exception as error:
            failed += 1
            print(f"FAILED: {dump_path}, frame {frame}", flush=True)
            print(f"Error: {error}\n", flush=True)

print("\nFeature extraction complete! :D", flush=True)
print(f"Total configurations: {total_configs}", flush=True)
print(f"Successfully written: {successful}", flush=True)
print(f"Failed: {failed}", flush=True)