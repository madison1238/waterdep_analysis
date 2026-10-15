import subprocess
import time
from datetime import datetime
import os



TOTAL_SIMS = 300
MAX_JOBS = 30
CHECK_INTERVAL = 60  # seconds

# starting
next_sim = 1

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
        print("Error checking queue:", flush=True)
        print(result.stderr, flush=True)
        return None

    jobs = result.stdout.strip().splitlines()

    return len(jobs)


def submit_simulation(sim_number):

    sim_directory = f"../sims/sim_{sim_number}/q6_validation"

    #print(f"Submitting simulation {sim_number}", flush=True)
    #print(f"Directory: {sim_directory}", flush=True)

    command = ["sbatch","sb.validation"]
    result = subprocess.run(command,capture_output=True,text=True,cwd=sim_directory)
    if result.returncode == 0:
        log(f"Submitted simulation {sim_number}")
        log(f"    {result.stdout.strip()}")
        return True

    else:
        log(f"ERROR submitting simulation {sim_number}")
        log(result.stderr.strip())
        return False


def main():
    global next_sim
    log("=" * 50)
    log("Starting simulation job manager")
    log("=" * 50)
    log(f"Total simulations: {TOTAL_SIMS}")
    log(f"Maximum jobs: {MAX_JOBS}")
    log(f"Check interval: {CHECK_INTERVAL} seconds")
    while next_sim <= TOTAL_SIMS:
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
            simulations_remaining = TOTAL_SIMS - next_sim + 1
            num_to_submit = min(available_slots,simulations_remaining)
            log(f"Submitting {num_to_submit} simulation(s)...")
            for _ in range(num_to_submit):
                success = submit_simulation(next_sim)
                if success:
                    next_sim += 1
                else:
                    log("Submission failed. " "Will retry later.")
                    break
        # Don't check again immediately
        time.sleep(CHECK_INTERVAL)
    log("")
    log("=" * 50)
    log("All simulations have been submitted!")
    log("=" * 50)
if __name__ == "__main__":
    main()