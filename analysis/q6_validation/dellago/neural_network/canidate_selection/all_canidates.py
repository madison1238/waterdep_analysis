import os
import csv


sims = 300
total = 0
for sim_num in range(sims):
    ice_file= f"sims/sim_{sim_num}/summary/ice_clusters.csv"
