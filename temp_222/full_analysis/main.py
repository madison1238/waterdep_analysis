from functions import get_first_passage_times
import csv
import os


sims = 5
sim_files = [f"../sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep = 5

all_first_passages = []
for file_name in sim_files:
    print(f"Processing {file_name}")
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
        mean_ns = mean_timestep * timestep * 1e-6
        mfpt[n] = mean_ns

    else:
        mfpt[n] = None

output_folder = '../summary'
os.makedirs(output_folder,exist_ok=True)
with open(f"{output_folder}/MFPT.csv", 'w', newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "n",
        "sim1_ns",
        "sim2_ns",
        "sim3_ns",
        "sim4_ns",
        "sim5_ns",
        "MFPT_ns"
    ])

    for n in range(min_n,max_n):
        row = [n]
        for sim in all_first_passages:
            timestep = sim[n]
        if timestep is not None:
            time_ns = timestep * timestep * 1e-6
            row.append(time_ns)
        else:
            row.append("")
        row.append(mfpt[n])
        writer.writerow(row)


