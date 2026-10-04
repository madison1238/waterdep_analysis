import matplotlib.pyplot as plt


timestep = 5
timesteps = []
vapor_molecules = []
condensed_molecules = []

with open("cluster_info.txt", 'r') as f:
    lines = f.readlines()

for line in lines:

    if "Cluster info at timestep" in line:
        cur_timestep = int(line.split()[-1].replace(':', ''))
        timesteps.append(cur_timestep * timestep)
    
    elif "Vapor atoms" in line:
        vapor_molecule_num = int(line.split()[-2])
        vapor_molecules.append(vapor_molecule_num)
    
    elif "Condensed Atoms" in line:
        condensed_molecule_num = int(line.split()[-2])
        condensed_molecules.append(condensed_molecule_num)

plt.figure()

plt.plot(timesteps, vapor_molecules, label="Vapor Molecules")
plt.plot(timesteps,condensed_molecules, label="Clustered Molecules")

plt.xlabel("Time (Femtoseconds)")
plt.ylabel("Number of molecules")
plt.title("Molecules vs Time")

plt.legend()
plt.savefig("Cluster_Vapor_Time.png")