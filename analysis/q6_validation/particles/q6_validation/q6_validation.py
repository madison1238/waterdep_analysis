from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import * 
from ovito.modifiers import ChillPlusModifier
from plots import *
from testing import *
import config
import os
import csv



frame = 0
target_id = 4093
os.makedirs(config.output, exist_ok=True)

output_file = f"{config.output}/single_particle_q4_q6_new.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "timestep",
        "particle_id",
        "phase",
        "q4_freud",
        "q6_freud",
        "q4_pyscal",
        "q6_pyscal"
    ])


    with open(config.dump, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()


                for i in range(num_atoms):
                    line = f.readline()

                    
                
                ids, positions, box, labels = load_frame(config.dump, frame, True)

                particle_values = track_particle_order(positions, box, ids, target_id)
                particle_phase = labels[particle_values["index"]]


                writer.writerow([
                    timestep,
                    target_id,
                    particle_phase,
                    particle_values["q4_freud"],
                    particle_values["q6_freud"],
                    particle_values["q4_pyscal"],
                    particle_values["q6_pyscal"]
                ])

                frame += 1

plot_particle_q4_q6(f"{config.output}/single_particle_q4_q6_new.csv", f"{config.output}/single_particle_q4_q6_new.png")

