from functions import get_MFPT
from plot import * 
import csv
import os


sims = 300
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep_inteveral = 5

all_MFPTs = []
for file_name in sim_files:
    print(f"Processing {file_name}", flush=True)
    simulation_MFPT = get_MFPT(file_name, min_n,max_n)
    all_MFPTs.append(simulation_MFPT)

mfpt = {}
for n in range(min_n, max_n + 1):
    times = []
    for sim in all_MFPTs:
        blocks = sim[n]
        for timestep in blocks:
            if timestep is not None:
                times.append(timestep)
    if len(times) > 0:
        mean_timestep = sum(times) / len(times)
        mean_ps = mean_timestep * timestep_inteveral * 1e-3
        mfpt[n] = mean_ps
    else:
        mfpt[n] = None

headers = ["n"]

for i in range(1, sims + 1):
    headers += [
        f"sim{i}_block1_ps",
        f"sim{i}_block2_ps",
        f"sim{i}_block3_ps",
        f"sim{i}_block4_ps"
    ]
headers.append("MFPT_ps")

output_folder = '../summary'
os.makedirs(output_folder,exist_ok=True)
with open(f"{output_folder}/MFPT.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for n in range(min_n, max_n + 1):
        row = [n]
        for sim in all_MFPTs:
            blocks = sim[n]
            for timestep in blocks:
                if timestep is not None:
                    time_ps = timestep * timestep_inteveral * 1e-3
                    row.append(time_ps)
                else:
                    row.append("")
        row.append(mfpt[n])
        writer.writerow(row)

plot_MFPT_v_n(f"../summary/MFPT_vs_n.png")
