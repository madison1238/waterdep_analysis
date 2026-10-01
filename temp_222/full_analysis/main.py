from functions import calculate_CN_pyscal
from plot import * 
import csv
import os


sims = 1
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep_inteveral = 5

calculate_CN_pyscal(1)

