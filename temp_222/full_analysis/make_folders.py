import os, shutil, re


sims = 5
all_seed1 = [12094904, 77822059, 10061298, 70923293, 91494557]
all_seed2 = [51174316, 97900584, 10818346, 76658347, 19632612]

for i in range(sims):
    sim_dir = f"sim_{i+1}"
    os.makedirs(sim_dir, exist_ok=True)
    seed1 = all_seed1[i]
    seed2 = all_seed2[i]
    shutil.copytree('./base', sim_dir, dirs_exist_ok=True)

    slurm_file = f"{sim_dir}/sb.water"
    lammps_file = f"{sim_dir}/in.template"

    #update slurm
    with open(slurm_file, 'r') as f:
        slurm_text = f.read()
    slurm_text = re.sub(r"\bNAME\b", f"sim_{i+1}", slurm_text)
    with open(slurm_file, 'w') as f:
        f.write(slurm_text)

    #update lammps
    with open(lammps_file, 'r') as f:
        lammps_text = f.read()
    lammps_text = re.sub(r"\brn1\b", str(seed1), lammps_text)
    lammps_text = re.sub(r"\brn2\b", str(seed2), lammps_text)
    with open(lammps_file, 'w') as f:
        f.write(lammps_text)