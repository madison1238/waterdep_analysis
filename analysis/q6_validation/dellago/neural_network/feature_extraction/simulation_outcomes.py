from pathlib import Path
import csv

SIMULATIONS_PATH = Path("..") / "configs" / "simulations"
OUTCOMES_PATH = Path("simulation_outcomes.csv")

fieldnames = [
    "config_id",
    "trial_id",
    "initial_n",
    "seed",
    "outcome",
    "crossing_timestep",
    "crossing_n",
    "total_steps",
    "chunks_completed"
]

results = []
failed = 0

config_folders = sorted(SIMULATIONS_PATH.iterdir())

total_trials = sum(
    1 for config in config_folders if config.is_dir()
    for trial in config.iterdir()
    if trial.is_dir() and (trial / "result.csv").exists()
)

print(f"Found {total_trials} result files.")
print("Collecting simulation outcomes...\n")

for config in config_folders:
    if not config.is_dir():
        continue
    config_id = config.name.split("_sim_")[0]
    for trial in sorted(config.iterdir()):
        result_path = trial / "result.csv"
        if not trial.is_dir() or not result_path.exists():
            continue
        try:
            with result_path.open("r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row["config_id"] = config_id
                    results.append(row)
                    print(
                        f"[{len(results)}/{total_trials}] "
                        f"Collected {config_id}, {trial.name}"
                    )
        except Exception as error:
            failed += 1
            print(f"FAILED: {result_path}")
            print(error)

with OUTCOMES_PATH.open("w", newline="") as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("\nCollection complete!")
print(f"Total results collected: {len(results)}")
print(f"Failed files: {failed}")
print(f"Expected results: {total_trials}")
