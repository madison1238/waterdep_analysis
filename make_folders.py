import re
import shutil
import os

sims = 5
all_seed1 = [59240277, 34986414, 21545117, 74196967, 24972974]
all_seed2 = [64356821, 52648704, 34095413, 21792018, 82737340]
for i in range(sims):
    sim_dir = f"./sim_{i+1}"
    os.makedirs(sim_dir, exist_ok=True)
    seed1 = all_seed1[i]
    seed2 = all_seed2[i]
    shutil.copytree('./base', sim_dir, dirs_exist_ok=True)


    lammps_stable_file = f"{sim_dir}/in.stable_template"
    lammps_deposit_file = f"{sim_dir}/in.template"

    #update lammps_stable_file
    with open(lammps_stable_file, 'r') as f:
        lammps_text = f.read()
    lammps_text = re.sub(r"\bSEED1\b", str(seed1), lammps_text)
    lammps_text = re.sub(r"\bSEED2\b", str(seed2), lammps_text)
    with open(lammps_stable_file, 'w') as f:
        f.write(lammps_text)

    #update lammps_deposit_file
    with open(lammps_deposit_file, 'r') as f:
        lammps_deposit_text = f.read()
    lammps_deposit_text = re.sub(r"\bSEED1\b", str(seed1), lammps_deposit_text)
    with open(lammps_deposit_file, 'w') as f:
        f.write(lammps_deposit_text)