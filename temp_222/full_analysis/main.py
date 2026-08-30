from functions import *




sims = 5
sim_files = [f"sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep = 5

all_first_passages = []
for file_name in sim_files:
    print(f"Processing {file_name}")
    first_passage = get_first_passage_times
