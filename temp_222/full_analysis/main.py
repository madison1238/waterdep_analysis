from functions import calculate_CN_pyscal
from plot import * 
import csv
import os


sims = 1
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep_inteveral = 5

pyscal_CN = calculate_CN_pyscal(1)

'''with open("pyscal_coordination.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["atom_index", "pyscal_cn"])
    for i, value in enumerate(pyscal_CN = calculate_CN_pyscal(1)):
        writer.writerow([i, value])'''

