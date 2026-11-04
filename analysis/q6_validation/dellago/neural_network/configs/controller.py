import os
import re
import csv
import time
import subprocess
from pathlib import Path
from datetime import datetime

from ovito.io import import_file
from ovito.modifiers import (
    VoronoiAnalysisModifier,
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier
)



CHUNK_STEPS = 1000
DUMP_INTERVAL = 100

MELT_THRESHOLD = 9
NUCLEATE_THRESHOLD = 61

MAX_TOTAL_STEPS = 1_000_000

INITIAL_INPUT = "in.config_restart"
CONTINUE_INPUT = "in.continue"

FIRST_SCRIPT = "sb.first"
CONTINUE_SCRIPT = "sb.continue"

DUMP_NAME = "dump.lammpstrj"
CURRENT_RESTART = "chunk.restart"
NEXT_RESTART = "chunk.next.restart"

KEEP_FINAL_DUMP = True




def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}", flush=True)



def get_trial_info():
    trial_dir = Path.cwd()
    config_id = trial_dir.parent.name
    trial_id = trial_dir.name
    match = re.search(r"_n(\d+)_", config_id)
    if match:
        initial_n = int(match.group(1))
    else:
        initial_n = None
    input_text = Path(INITIAL_INPUT).read_text()
    seed_match = re.search(
        r"variable\s+seed\s+equal\s+(\d+)",
        input_text
    )
    if not seed_match:
        raise ValueError(
            "Could not find the random seed in in.config"
        )
    seed = int(seed_match.group(1))
    return {
        "config_id": config_id,
        "trial_id": trial_id,
        "initial_n": initial_n,
        "seed": seed
    }




def submit_job(script_name, chunk_steps):
    result = subprocess.run(
        [
            "sbatch",
            "--parsable",
            f"--export=ALL,CHUNK_STEPS={chunk_steps},"
            f"DUMP_FILE={DUMP_NAME},"
            f"DUMP_INTERVAL={DUMP_INTERVAL}",
            script_name
        ],
        capture_output=True,
        text=True,
        check=True
    )

    job_id = result.stdout.strip().split(";")[0]
    log(f"Submitted {script_name}. Job ID: {job_id}")
    return job_id


def wait_for_job(job_id):
    log(f"Waiting for job {job_id}...")
    while True:
        result = subprocess.run(
            ["squeue", "-h", "-j", job_id, "-o", "%T"],
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            break
        time.sleep(5)
    while True:
        result = subprocess.run(
            [
                "sacct",
                "-n",
                "-X",
                "-j", job_id,
                "--format=State"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        states = [
            line.strip().split()[0]
            for line in result.stdout.splitlines()
            if line.strip()
        ]
        if states:
            state = states[0].split("+")[0]
            if state == "COMPLETED":
                log(f"Job {job_id} completed successfully.")
                return
            raise RuntimeError(
                f"Job {job_id} failed. Final state: {state}"
            )
        time.sleep(5)


# --------------------------------------------------
# RUN ONE LAMMPS CHUNK
# --------------------------------------------------

def run_lammps(input_file, current_chunk_steps):

    dump_path = Path(DUMP_NAME)
    next_restart = Path(NEXT_RESTART)

    # Remove outputs left over from a previous chunk.
    if dump_path.exists():
        dump_path.unlink()

    if next_restart.exists():
        next_restart.unlink()

    # Choose the appropriate Slurm script.
    if input_file == INITIAL_INPUT:
        script_name = FIRST_SCRIPT
    else:
        script_name = CONTINUE_SCRIPT

    # Submit the job.
    job_id = submit_job(
        script_name,
        current_chunk_steps
    )

    # Wait for successful completion.
    wait_for_job(job_id)

    # Verify the expected files exist.
    if not dump_path.exists():
        raise RuntimeError(
            f"LAMMPS did not create {DUMP_NAME}"
        )

    if not next_restart.exists():
        raise RuntimeError(
            f"LAMMPS did not create {NEXT_RESTART}"
        )

    log("LAMMPS chunk completed successfully.")


# --------------------------------------------------
# OVITO DUMP ANALYSIS
# --------------------------------------------------

def analyze_dump(dump_path):

    pipeline = import_file(
        str(dump_path),
        multiple_frames=True
    )

    log(f"Frames found: {pipeline.source.num_frames}")

    # Voronoi analysis.
    pipeline.modifiers.append(
        VoronoiAnalysisModifier(
            relative_face_threshold=0.02
        )
    )

    # CHILL+ structure classification.
    pipeline.modifiers.append(
        ChillPlusModifier(cutoff=3.5)
    )

    # Select Ih and Ic particles.
    pipeline.modifiers.append(
        ExpressionSelectionModifier(
            expression="StructureType == 1 || StructureType == 2"
        )
    )

    # Cluster analysis.
    pipeline.modifiers.append(
        ClusterAnalysisModifier(
            cutoff=3.5,
            sort_by_size=True,
            only_selected=True
        )
    )

    frame_results = []

    # Analyze every frame in chronological order.
    for frame in range(pipeline.source.num_frames):

        data = pipeline.compute(frame)

        largest_cluster = int(
            data.attributes.get(
                "ClusterAnalysis.largest_size",
                0
            )
        )

        timestep = int(data.attributes["Timestep"])

        frame_results.append({
            "timestep": timestep,
            "largest_cluster": largest_cluster
        })

    return frame_results


# --------------------------------------------------
# CHECK MELTING / NUCLEATION
# --------------------------------------------------

def check_outcome(frame_results):

    for result in frame_results:

        n = result["largest_cluster"]

        if n <= MELT_THRESHOLD:

            return {
                "outcome": "melted",
                "crossing_timestep": result["timestep"],
                "crossing_n": n
            }

        elif n >= NUCLEATE_THRESHOLD:

            return {
                "outcome": "nucleated",
                "crossing_timestep": result["timestep"],
                "crossing_n": n
            }

    return None


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

def save_result(result):

    result_file = Path("result.csv")

    with result_file.open("w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=result.keys()
        )

        writer.writeheader()
        writer.writerow(result)

    log(f"Result saved to {result_file}")


# --------------------------------------------------
# MAIN TRAJECTORY CONTROLLER
# --------------------------------------------------

def run_trajectory():

    # Make sure the Slurm output directory exists.
    Path("outputs").mkdir(exist_ok=True)

    info = get_trial_info()

    log("=" * 55)
    log(f"Starting {info['config_id']} / {info['trial_id']}")
    log(f"Initial cluster size: {info['initial_n']}")
    log(f"Random seed: {info['seed']}")
    log("=" * 55)

    total_steps = 0
    chunk_number = 0
    outcome = None

    input_file = INITIAL_INPUT

    while total_steps < MAX_TOTAL_STEPS:

        # Prevent the final chunk from exceeding the limit.
        current_chunk_steps = min(
            CHUNK_STEPS,
            MAX_TOTAL_STEPS - total_steps
        )

        log(
            f"Starting chunk {chunk_number + 1} "
            f"({total_steps}/{MAX_TOTAL_STEPS} steps completed)"
        )

        # Submit and wait for the LAMMPS job.
        run_lammps(
            input_file,
            current_chunk_steps
        )

        # Count the successfully completed simulation steps.
        total_steps += current_chunk_steps
        chunk_number += 1

        # Analyze the dump.
        frame_results = analyze_dump(DUMP_NAME)

        if not frame_results:
            raise RuntimeError("No frames found in dump.")

        latest_n = frame_results[-1]["largest_cluster"]

        log(
            f"Chunk {chunk_number} complete. "
            f"Latest largest cluster: {latest_n}"
        )

        # Check every frame for the first observed crossing.
        outcome = check_outcome(frame_results)

        # Promote the new restart after successful analysis.
        os.replace(NEXT_RESTART, CURRENT_RESTART)

        if outcome is not None:

            log(
                f"TRAJECTORY FINISHED: "
                f"{outcome['outcome'].upper()}"
            )

            log(
                f"First crossing timestep: "
                f"{outcome['crossing_timestep']}"
            )

            log(
                f"Cluster size at crossing: "
                f"{outcome['crossing_n']}"
            )

            break

        # Remove the dump before the next chunk.
        if not KEEP_FINAL_DUMP:
            Path(DUMP_NAME).unlink()

        # All subsequent chunks use the continuation input.
        input_file = CONTINUE_INPUT

    # Maximum simulation length reached without crossing.
    if outcome is None:

        outcome = {
            "outcome": "max_steps",
            "crossing_timestep": None,
            "crossing_n": None
        }

        log(
            "Maximum trajectory length reached "
            "without crossing."
        )

    # Collect final results.
    result = {
        **info,
        "outcome": outcome["outcome"],
        "crossing_timestep": outcome["crossing_timestep"],
        "crossing_n": outcome["crossing_n"],
        "total_steps": total_steps,
        "chunks_completed": chunk_number
    }

    save_result(result)

    log("=" * 55)

    return result


# --------------------------------------------------
# START
# --------------------------------------------------

if __name__ == "__main__":

    try:
        run_trajectory()

    except Exception as error:

        log(f"ERROR: {error}")

        raise
