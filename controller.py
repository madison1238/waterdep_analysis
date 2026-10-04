import os
import subprocess
import time
import matplotlib.pyplot as plt


def submit_job(script_name):
    result = subprocess.run(
        ['sbatch', script_name],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    job_id = output.split()[-1]
    return job_id

def wait_for_job(job_id):
    while True:
        result = subprocess.run(
            ['squeue', '-j', job_id ],
            capture_output=True,
            text=True
        )

        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:
            break
        time.sleep(3)

def density_to_g_m3(density_molecules_A3):
    avogadro = 6.022e23
    water_molar_mass = 18.015
    A3_per_m3 = 1e30

    moles_per_A3 = density_molecules_A3/avogadro
    grams_per_A3 = moles_per_A3 * water_molar_mass
    density_g_m3 = grams_per_A3 * A3_per_m3

    return density_g_m3

def g_m3_to_molecule_A3(g_m3):
    avogadro = 6.022e23
    water_molar_mass = 18.015
    A3_per_m3 = 1e30

    mol_per_m3 = g_m3 / water_molar_mass
    molecules_per_m3 = mol_per_m3 * avogadro
    molecules_per_A3 = molecules_per_m3 / A3_per_m3
    return molecules_per_A3



def cluster_info(dump_file, output_file, box_length):
    latest_clusters = {}
    latest_timestep = None
    with open (dump_file, 'r') as f:
        found_timestep = False
        num_atoms = 0
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
                latest_timestep = timestep

                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                clusters = {}

                for i in range(num_atoms):
                    atoms_line = f.readline().split()
                    atom_id = int(atoms_line[0])
                    cluster_id = int(float(atoms_line[5]))

                    if cluster_id not in clusters:
                        clusters[cluster_id] = 1
                    else:
                        clusters[cluster_id] += 1
                latest_clusters = clusters
    if latest_timestep is None:
        return None
    else:

        sorted_clusters = sorted(
        latest_clusters.items(),
        key=lambda x: x[1],
        reverse=True
        )

        vapor_molecules = 0
        condensed_molecules = 0

        for cluster_id, size in sorted_clusters:
            if size < 3:
                vapor_molecules += size
            else:
                condensed_molecules += size

        total_volume = box_length ** 3 #Angstroms^3
        volume_per_molecule = 30.0 #A^3 
        cluster_volume = condensed_molecules * volume_per_molecule
        free_volume = total_volume - cluster_volume
        vapor_density = vapor_molecules / free_volume # molecules per A^3
        vapor_density_g_m3 = density_to_g_m3(vapor_density)


        


        with open(output_file, 'a') as f:
            f.write(f"\nCluster info at timestep {latest_timestep}:\n")
            f.write(f"Total number of clusters: {len(latest_clusters)}\n")
            f.write(f"Largest cluster size: {sorted_clusters[0][1]} atoms\n")
            f.write(f"Vapor atoms (size < 3): {vapor_molecules} atoms\n")
            f.write(f"Condensed Atoms: {condensed_molecules} atoms\n")
            f.write(f"Vapor density: {vapor_density:.8e} molecules/A^3\n")
            f.write(f"Vapor density: {vapor_density_g_m3:.8e} grams/m^3\n")
            f.write(f"Cluster sizes at timestep {latest_timestep}:\n")
            for cluster_id, size in sorted_clusters:
                f.write(f"Cluster {cluster_id}: {size} atoms\n")
        return (
            vapor_molecules,
            condensed_molecules,
            vapor_density,
            free_volume
        )

def calculate_start_temperature(start,end,cycles,current_cycle):
    fraction_complete = current_cycle/cycles
    return start - ((start - end) * fraction_complete)

def calculate_end_temperature(start,end,cycles,current_cycle):
    fraction_complete = current_cycle/cycles
    goal_fraction = fraction_complete + (1/cycles)
    return start - ((start-end) * goal_fraction)

def calculate_duration( cycles, total_steps):
    return total_steps * (1/cycles)

def calculate_restart_step(current_cycle,cycles,total_steps):
    interval = total_steps / cycles
    return current_cycle * interval

def calculate_final_step(current_cycle,cycles,total_steps):
    interval = total_steps / cycles
    return (current_cycle+1) * interval

def calculate_missing_molecules(vapor_molecules, target_density, free_volume):
    gain = 3.0
    target_molecules = target_density * free_volume
    missing_molecules = gain * (target_molecules - vapor_molecules)
    return max(0, int(missing_molecules))


def calculate_insertion_frequency(missing_atoms):
    if missing_atoms <= 0:
        return 1000000
    scale_factor = 10000
    frequency = int(scale_factor / missing_atoms)
    frequency = max(1, frequency)
    return frequency


def graph_density(all_timesteps,all_density):
    plt.figure()
    plt.plot(all_timesteps,all_density, marker="o")
    plt.title("Vapor Density vs Time")
    plt.xlabel("Time (Femtoseconds)")
    plt.ylabel("Vapor Density (g/m³)")
    plt.savefig("timestep_vs_density.png")


def main():
    #box_length = 1126 # Angstroms
    timestep = 5

    #target ss ratio
    s = 100000
    #number of atoms
    nW = 52000

    base_density = g_m3_to_molecule_A3(0.002)
    target_density = base_density * s

    box_volume = nW / target_density
    box_length = box_volume ** (1/3)

    print(f"S: {s}", flush=True)
    print(f"Starting atoms: {nW}", flush=True)
    print(f"Target density: {target_density:.8e} molecules/A^3", flush=True)
    print(f"Target density: {density_to_g_m3(target_density):.8e} g/m^3", flush=True)
    print(f"Box volume: {box_volume:.8e} A^3", flush=True)
    print(f"Box length: {box_length:.2f} A", flush=True)

    cycles = 20
    start_temp = 200
    end_temp = 200
    total_steps = 1000000
    all_vapor_density_g_m3 = []
    vapor_molecules = nW
    free_volume = box_length ** 3

    all_timesteps = []

    density_log = "density_log.txt"
    cluster_log = "cluster_info.txt"

   
    os.makedirs("restarts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    for cycle in range(cycles):
        filename = f"dumps/dump.{cycle}.lammpstrj"
        if os.path.exists(filename):
            os.remove(filename)

    with open("in.stable_template", 'r') as stable:
        stable_file = stable.read()
    stable_file = stable_file.replace("TEMP", str(start_temp))
    stable_file = stable_file.replace("NW", str(nW))
    stable_file = stable_file.replace("HL", str(box_length/2))

    with open("in.stable", 'w') as stable:
        stable.write(stable_file)



    stable_id = submit_job('sb.stable')
    wait_for_job(stable_id)

    
    with open(density_log, 'w') as log:
        log.write("DENSITY LOG FILE\n")
        log.write("===================\n\n")
    
    '''with open(cluster_log, 'w') as log:
        log.write("CLUSTER LOG FILE\n")
        log.write("===================\n\n")'''

    for cycle in range(cycles):
        with open("in.template", 'r') as f:
            template = f.read()

        
        missing_atoms = calculate_missing_molecules(
            vapor_molecules,
            target_density,
            free_volume
        )
        insertion_frequency = calculate_insertion_frequency(missing_atoms)
        
        input_script = template.replace("LIMIT", str(missing_atoms))
        input_script = input_script.replace("HL", str(box_length/2))
        input_script = input_script.replace("FREQUENCY", str(insertion_frequency))
        input_script = input_script.replace("CYCLE_NUM", str(cycle))
        input_script = input_script.replace("DUR2", str(int(calculate_duration(cycles, total_steps))))
        if cycle == 0:
            input_script = input_script.replace("deposit.LAST_CYCLE", 'stable')
        else:
            input_script = input_script.replace("LAST_CYCLE", str(int(calculate_restart_step(cycle,cycles,total_steps))))
        input_script = input_script.replace("END_CYCLE", str(int(calculate_final_step(cycle,cycles,total_steps))))
        input_script = input_script.replace("START_TEMP", str(calculate_start_temperature(start_temp,end_temp,cycles, cycle)))
        input_script = input_script.replace("END_TEMP", str(calculate_end_temperature(start_temp,end_temp,cycles, cycle)))
        with open("in.deposit", 'w') as f:
            f.write(input_script)
        

        deposit_id = submit_job('sb.deposit')
        wait_for_job(deposit_id)


        cycle_dump = f"dumps/dump.{cycle}.lammpstrj"
        (vapor_molecules,
        condensed_molecules,
        vapor_density,
        free_volume) = cluster_info(cycle_dump, cluster_log, box_length)
        all_vapor_density_g_m3.append(density_to_g_m3(vapor_density))
        all_timesteps.append(calculate_restart_step(cycle + 1,cycles,total_steps) * timestep)


        with open(density_log, 'a') as log:
            log.write(f"Cycle: {cycle}\n")
            log.write(f"Target Density: {target_density:.8e} molecules/A^3\n")
            log.write(f"Target Density: {density_to_g_m3(target_density):.8e} grams/m^3\n")
            log.write(f"Vapor Density: {vapor_density:.8e} molecules/A^3\n")
            log.write(f"Vapor Density: {density_to_g_m3(vapor_density):.8e} grams/m^3\n")
            log.write(f"Missing atoms (atom limit): {missing_atoms}\n")
            log.write(f"Deposition Rate (timesteps to deposit): {insertion_frequency}\n\n")

    graph_density(all_timesteps,all_vapor_density_g_m3)
if __name__ == "__main__":
    main()


