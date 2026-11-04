
import csv
from pathlib import Path
import shutil
import re
import random

SCRIPT_DIR = Path(__file__).resolve().parent

SIM_DIR = SCRIPT_DIR / 'simulations'
BASE_DIR = SCRIPT_DIR/ 'base'

CONFIGURATIONS = (SCRIPT_DIR / ".." / "canidate_selection").resolve()

ALL_SELECTED_CONFIG_SIMS = CONFIGURATIONS / 'starting_configs'
SELECTED_CONFIGS =  CONFIGURATIONS / 'selected_configs.csv'

RESTART_NAME = "restart.config"

TRIALS = 10


def get_simulation_directory(dump_path):
    dump_file = Path(dump_path)
    return dump_file.resolve().parent


def make_seeds(number):
    return random.sample(range(10_000_000, 100_000_001), number)

def create_input_script(input_path, seed):
    with open(input_path, "r") as f:
        input_text = f.read()

    input_text = re.sub(
        r"\bSEED1\b",
        str(seed),
        input_text
    )

    with open(input_path, "w") as f:
        f.write(input_text)


def update_slurm_script(slurm_path, job_name):
    with open(slurm_path, "r") as f:
        slurm_text = f.read()

    slurm_text = re.sub(
        r"\bNAME\b",
        job_name,
        slurm_text
    )

    with open(slurm_path, "w") as f:
        f.write(slurm_text)

def update_controller(path, job_name):
    with open(path, "r") as f:
        controller_text = f.read()
    controller_text = re.sub(
        r"\bNAME\b",
        f"control_{job_name}",
        controller_text
        )
    
    with open(path, "w") as f:
        f.write(controller_text)

def prepare_folders():

    selected_rows = []
    with SELECTED_CONFIGS.open(newline="") as csv_file:

        reader = csv.DictReader(csv_file)

        required_columns = {
            "Dump Path",
            "Frame",
            "Timestep",
            "Largest Cluster Size (n)",
            "Size Bin"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV is missing required columns: "
                f"{required_columns - set(reader.fieldnames or [])}"
            )

        for row_number, row in enumerate(reader, start=1):
            try:
                dump_path = row["Dump Path"]
                timestep = int(row["Timestep"])
                cluster_size = int(row["Largest Cluster Size (n)"])
                sim_dir = get_simulation_directory(dump_path)
                sim_name = sim_dir.name
                config_name = (
                    f"config_{row_number:03d}_"
                    f"{sim_name}_n{cluster_size}_t{timestep}"
                )
                restart = (
                    ALL_SELECTED_CONFIG_SIMS
                    / config_name
                    / RESTART_NAME
                )
                if not restart.is_file():
                    raise FileNotFoundError(
                        f"Restart not found: {restart}"
                    )
                selected_rows.append({
                    "config_name": config_name,
                    "restart": restart,
                    "row_number": row_number
                })
            except Exception as error:
                print(
                    f"ERROR CSV row {row_number}: {error}",
                    flush=True)
                raise
    if not selected_rows:
        raise RuntimeError("No valid configurations found!")

    total_trials = len(selected_rows) * TRIALS
    seeds = make_seeds(total_trials)


    SIM_DIR.mkdir(parents=True, exist_ok=True)

    seed_index = 0
    created = 0
    for config in selected_rows:
        config_name = config["config_name"]
        restart = config["restart"]
        print(f"Preparing {config_name}", flush=True)
        config_all_trials = SIM_DIR / config_name
        config_all_trials.mkdir(exist_ok=True)

        for i in range(TRIALS):
            trial_name = f"trial_{i+1}"
            single_trial = config_all_trials / trial_name
            single_trial.mkdir(exist_ok=True)

            shutil.copytree(
                BASE_DIR,
                single_trial,
                dirs_exist_ok=True
            )

            shutil.copyfile(
                restart,
                single_trial / RESTART_NAME
            )


            random_seed = seeds[seed_index]
            seed_index += 1


            slurm_start = single_trial / "sb.first" 
            slurm_continue = single_trial / "sb.continue"
            controller = single_trial / "controller.py"
            job_name = f"config_{config['row_number']:03d}_t_{i+1}"
            update_slurm_script(slurm_start, job_name)
            update_slurm_script(slurm_continue, job_name)
            update_controller(controller,job_name)


            input_file = single_trial / "in.config_restart"
            create_input_script(input_file, random_seed)
            created += 1

    print("\nPreparation complete!")
    print(f"Configurations: {len(selected_rows)}")
    print(f"Trials per configuration: {TRIALS}")
    print(f"Total trials created: {created}")

if __name__ == "__main__":
    prepare_folders()





                

                


