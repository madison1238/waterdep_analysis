import subprocess
import time
from datetime import datetime
import os



TOTAL_SIMS = 57
MAX_JOBS = 30
CHECK_INTERVAL = 60  # seconds
SUBMITTED_FILE = "submitted_sims.txt"

ss_ratios = [100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000]
temps =  [180,190,200,210,220,230,240]

# starting
next_sim = 1

def log(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)

def load_submitted():
    if not os.path.exists(SUBMITTED_FILE):
        return set()

    with open(SUBMITTED_FILE, "r") as file:
        return {line.strip() for line in file if line.strip()}

def save_submitted(sim_key):
    with open(SUBMITTED_FILE, "a") as file:
        file.write(sim_key + "\n")


def get_my_job_count():
    username = os.environ["USER"]
    result = subprocess.run(
        ["squeue", "-u", username, "-h"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Error checking queue:", flush=True)
        print(result.stderr, flush=True)
        return None

    jobs = result.stdout.strip().splitlines()
    return len(jobs)


def submit_simulation(temp,ss_ratio):
    sim_key = f"ss_{ss_ratio}/temp_{temp}"
    sim_directory = f"../sims/ss_{ss_ratio}/temp_{temp}"

    command = ["sbatch","sb.controller"]
    result = subprocess.run(command,capture_output=True,text=True,cwd=sim_directory)
    if result.returncode == 0:
        log(f"Submitted simulation ss_{ss_ratio}/temp_{temp}")
        log(f"    {result.stdout.strip()}")
        return True

    else:
        log(f"ERROR submitting simulation ss_{ss_ratio}/temp_{temp}")
        log(result.stderr.strip())
        return False


def main():
    submitted = load_submitted()
    simulations = [(ss_ratio, temp) for ss_ratio in ss_ratios for temp in temps]
    log("=" * 50)
    log("Starting simulation job manager")
    log("=" * 50)
    log(f"Total simulations: {TOTAL_SIMS}")
    log(f"Already submitted: {len(submitted)}")
    log(f"Maximum jobs: {MAX_JOBS}")
    log(f"Check interval: {CHECK_INTERVAL} seconds")
    log("=" * 50)

    while True:
        pending = [(ss_ratio, temp) for ss_ratio in ss_ratios for temp in temps if f"ss_{ss_ratio}/temp_{temp}" not in submitted]

        if not pending:
            break
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
            num_to_submit = min(available_slots, len(pending))
            log(f"Submitting {num_to_submit} simulation(s)...")
            for ss_ratio, temp in pending[:num_to_submit]:
                sim_key = f"ss_{ss_ratio}/temp_{temp}"
                success = submit_simulation(temp, ss_ratio)
                if success:
                    submitted.add(sim_key)
                    save_submitted(sim_key)
                else:
                    log("Submission failed. " "Will retry later.")
                    break
        log(f"Completed submissions: {len(submitted)}/{len(simulations)}")
        time.sleep(CHECK_INTERVAL)
    log("")
    log("=" * 50)
    log("All simulations have been submitted!")
    log("=" * 50)
if __name__ == "__main__":
    main()