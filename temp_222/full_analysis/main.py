from functions import get_first_passage_times
from plot import * 
import csv
import os


sims = 300
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep_inteveral = 5

all_first_passages = []
for file_name in sim_files:
    print(f"Processing {file_name}", flush=True)
    first_passage = get_first_passage_times(file_name, min_n,max_n)
    all_first_passages.append(first_passage)

mfpt = {}
for n in range(min_n, max_n+1):
    times = []
    for sim in all_first_passages:
        timestep = sim[n]
        if timestep is not None:
            times.append(timestep)
    if len(times) > 0:
        mean_timestep = sum(times) / len(times)
        mean_ps = mean_timestep * timestep_inteveral * 1e-3
        mfpt[n] = mean_ps

    else:
        mfpt[n] = None

output_folder = '../summary'
os.makedirs(output_folder,exist_ok=True)
with open(f"{output_folder}/MFPT.csv", 'w', newline="") as file:
    writer = csv.writer(file)

    writer.writerow(
    ["n"] +
    [f"sim{i}_ps" for i in range(1, sims + 1)] +
    ["MFPT_ps"]
)

    for n in range(min_n,max_n+1):
        row = [n]
        for sim in all_first_passages:
            timestep = sim[n]
            if timestep is not None:
                time_ps = timestep * timestep_inteveral * 1e-3
                row.append(time_ps)
            else:
                row.append("")
        row.append(mfpt[n])
        writer.writerow(row)

plot_MFPT_v_n(f"../summary/MFPT_vs_n.png")