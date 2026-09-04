import functions
from plot import * 
import csv
import os


sims = 1
source_dir = '../base/q6_validation'

for i in range(1, sims+1):
    dest_dir = f"../sims/sim_{i}"
    functions.copy_to_folder(source_dir,dest_dir)