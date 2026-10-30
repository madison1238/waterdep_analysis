
import subprocess
import time
from datetime import datetime
from pathlib import Path
import os


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "starting_configs"

MAX_JOBS = 30
CHECK_INTERVAL = 60  # seconds


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def log(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)


def get_my_job_count():

    username = os.environ["USER"]

    result = subprocess.run(
        ["squeue", "-u", username, "-h"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log("Error checking queue:")
        log(result.stderr)
        return None

    jobs = result.stdout.strip().splitlines()

    return len(jobs)


def submit_simulation(config_directory):

    config_name = config_directory.name

    command = ["sbatch", "sb.water"]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=config_directory
    )

    if result.returncode == 0:
        log(f"Submitted {config_name}")
        log(f"    {result.stdout.strip()}")
        return True

    else:
        log(f"ERROR submitting {config_name}")
        log(result.stderr.strip())
        return False


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    log("=" * 50)
    log("Starting configuration job manager")
    log("=" * 50)

    # Find all configuration directories
    config_directories = sorted(
        path for path in CONFIG_DIR.glob("config_*")
        if path.is_dir()
    )

    total_configs = len(config_directories)

    if total_configs == 0:
        log(f"No configuration folders found in {CONFIG_DIR}")
        return

    log(f"Total configurations: {total_configs}")
    log(f"Maximum jobs: {MAX_JOBS}")
    log(f"Check interval: {CHECK_INTERVAL} seconds")
    log(f"Configuration directory: {CONFIG_DIR}")

    next_config = 0

    while next_config < total_configs:

        log("")
        log("Checking Slurm queue...")

        job_count = get_my_job_count()

        if job_count is None:
            log("Could not determine queue size.")
            log("Waiting before trying again...")
            time.sleep(CHECK_INTERVAL)
            continue

        log(f"Current jobs: {job_count}/{MAX_JOBS}")

        available_slots = MAX_JOBS - job_count

        if available_slots <= 0:

            log("Queue is full.")
            log(f"Waiting {CHECK_INTERVAL} seconds...")

        else:

            configs_remaining = total_configs - next_config

            num_to_submit = min(
                available_slots,
                configs_remaining
            )

            log(f"Submitting {num_to_submit} configuration(s)...")

            for _ in range(num_to_submit):

                config_directory = config_directories[next_config]

                # Verify that the SLURM script exists
                if not (config_directory / "sb.water").exists():
                    log(f"ERROR: sb.water not found in {config_directory}")
                    next_config += 1
                    continue

                success = submit_simulation(config_directory)

                if success:
                    next_config += 1

                else:
                    log("Submission failed. Will retry later.")
                    break

        time.sleep(CHECK_INTERVAL)

    log("")
    log("=" * 50)
    log("All configurations have been submitted!")
    log("=" * 50)


if __name__ == "__main__":
    main()
