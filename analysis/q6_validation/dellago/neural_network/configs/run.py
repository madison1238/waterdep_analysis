import subprocess
import time
from datetime import datetime
from pathlib import Path
import os


SCRIPT_DIR = Path(__file__).resolve().parent
SIMULATION_DIR = SCRIPT_DIR / "simulations"
MAX_JOBS = 13
CHECK_INTERVAL = 60  # seconds


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


def submit_trial(trial_directory):
    command = ["sbatch", "sb.controller"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=trial_directory
    )
    if result.returncode == 0:
        log(f"Submitted {trial_directory.parent.name}/{trial_directory.name}")
        log(f"    {result.stdout.strip()}")
        return True
    else:
        log(f"ERROR submitting {trial_directory}")
        log(result.stderr.strip())
        return False


def main():
    log("=" * 50)
    log("Starting simulation trial job manager")
    log("=" * 50)
    config_directories = sorted(
        path for path in SIMULATION_DIR.glob("config_*")
        if path.is_dir()
    )

    if not config_directories:
        log(f"No configurations found in {SIMULATION_DIR}")
        return

    trial_directories = []
    for config_directory in config_directories:
        trials = sorted(
            config_directory.glob("trial_*")
        )
        for trial_directory in trials:
            if trial_directory.is_dir():
                trial_directories.append(trial_directory)
    total_configs = len(config_directories)
    total_trials = len(trial_directories)
    log(f"Total configurations: {total_configs}")
    log(f"Total trial folders: {total_trials}")
    log(f"Maximum jobs: {MAX_JOBS}")
    log(f"Check interval: {CHECK_INTERVAL} seconds")

    next_trial = 0
    submitted = 0

    while next_trial < total_trials:

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

            num_to_submit = min(
                available_slots,
                total_trials - next_trial
            )

            log(f"Submitting {num_to_submit} trial(s)...")

            for _ in range(num_to_submit):

                trial_directory = trial_directories[next_trial]

                controller = trial_directory / "sbatch.controller"

                if not controller.exists():
                    log(f"ERROR: sbatch.controller not found in {trial_directory}")
                    next_trial += 1
                    continue

                success = submit_trial(trial_directory)

                if success:
                    submitted += 1
                    next_trial += 1

                else:
                    log("Submission failed. Will retry later.")
                    break

        log(f"Progress: {submitted}/{total_trials} submitted")

        time.sleep(CHECK_INTERVAL)

    log("")
    log("=" * 50)
    log("All trial jobs have been submitted!")
    log(f"Configurations: {total_configs}")
    log(f"Trials submitted: {submitted}/{total_trials}")
    log("=" * 50)


if __name__ == "__main__":
    main()