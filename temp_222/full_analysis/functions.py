import csv
import os
import shutil


def femtoseconds_to_picoseconds(fs, ts):
    return fs * ts * 0.001



def get_first_passage_times(filename, min_n, max_n):
    first_passage = {}

    for n in range(min_n, max_n + 1):
        first_passage[n] = None
    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestep = int(row["timestep"])
            largest_cluster = int(row["largest_cluster"])
            for n in range(min_n, max_n + 1):
                if first_passage[n] is None and largest_cluster >= n:
                    first_passage[n] = timestep
    return first_passage


# read csv to get times and largest clusters
def read_simulation(filename):
    times = []
    largest_clusters = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestep = int(row["timestep"])
            largest_cluster = int(row["largest_cluster"])
            time_ps = femtoseconds_to_picoseconds(timestep, 5)
            times.append(time_ps)
            largest_clusters.append(largest_cluster)
    return times, largest_clusters


#find times at which largest cluster reaches threshold
#crossing is when size has moved away from threshold +-
def find_crossings(times, cluster_sizes, n):
    crossing_times = []
    for i in range(1, len(cluster_sizes)):
        previous_size = cluster_sizes[i - 1]
        current_size = cluster_sizes[i]
        # Crossing from below n to above n
        crossed_up = previous_size < n and current_size >= n
        # Crossing from above n to below n
        crossed_down = previous_size > n and current_size <= n
        if crossed_up or crossed_down:
            crossing_times.append(times[i])
    return crossing_times

def calculate_recurrence_times(crossing_times):
    recurrence_times = []
    for i in range(1, len(crossing_times)):
        time = crossing_times[i] - crossing_times[i - 1]
        recurrence_times.append(time)

    return recurrence_times

def calculate_blocks(recurrence_times):
    block_size = 4
    """
    Block 1 = 1-4
    Block 2 = 5-8
    Block 3 = 9-12
    Block 4 = 13-16
    """
    blocks = []
    for block_number in range(4):
        start = block_number * block_size
        end = start + block_size
        block = recurrence_times[start:end]

        # complete blocks of 4
        if len(block) == block_size:
            mean = sum(block) / block_size
            blocks.append(mean)
        else:
            blocks.append(None)

    return blocks

def process_simulation(filename, min_n, max_n):
    """
    Calculate the four recurrence-time blocks
    for every threshold n.
    """
    times, cluster_sizes = read_simulation(filename)
    results = {}
    for n in range(min_n, max_n + 1):
        crossings = find_crossings(times,cluster_sizes,n)
        recurrence_times = calculate_recurrence_times(crossings)
        blocks = calculate_blocks(recurrence_times)
        results[n] = blocks
    return results


def copy_to_folder(source_path, destination_folder):
    os.makedirs(destination_folder,exist_ok=True)
    if os.path.isfile(source_path):
        shutil.copy2(source_path, destination_folder)

    elif os.path.isdir(source_path):
        destination = os.path.join(
            destination_folder,
            os.path.basename(source_path)
        )

        shutil.copytree(
            source_path,
            destination,
            dirs_exist_ok=True
        )

    else:
        raise FileNotFoundError(
            f"Source does not exist: {source_path}"
        )

