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
    q6_values = []
    q4_values = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestep = int(row["timestep"])
            largest_cluster = int(row["largest_cluster"])
            q6 = float(row["q6"])
            q4 = float(row["q4"])
            time_ps = femtoseconds_to_picoseconds(timestep, 5)
            times.append(time_ps)
            largest_clusters.append(largest_cluster)
    return times, largest_clusters, q6_values, q4_values


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

def find_crossing_indices(cluster_sizes, n):
    crossing_indices = []
    for i in range(1, len(cluster_sizes)):
        previous_size = cluster_sizes[i - 1]
        current_size = cluster_sizes[i]
        # Crossing from below n to above n
        crossed_up = previous_size < n and current_size >= n
        # Crossing from above n to below n
        crossed_down = previous_size > n and current_size <= n
        if crossed_up or crossed_down:
            crossing_indices.append([i])
    return crossing_indices



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



def calculate_blocks_parameters(values):
    block_size = 4
    blocks = []
    for block_number in range(4):
        start = block_number * block_size
        end = start + block_size
        block = values[start:end]
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


def process_simulation_parameters(filename, min_n, max_n):

    """
    Calculate the four Q6 and Q4 blocks
    for every threshold n.
    """
    times, cluster_sizes, q6_values, q4_values = read_simulation(filename)
    results = {}
    for n in range(min_n, max_n + 1):
        crossing_indices = find_crossing_indices(cluster_sizes, n)
        crossing_q6 = []
        crossing_q4 = []
        for index in crossing_indices:
            crossing_q6.append(q6_values[index])
            crossing_q4.append(q4_values[index])
        q6_blocks = calculate_blocks_parameters(crossing_q6)
        q4_blocks = calculate_blocks_parameters(crossing_q4)
        results[n] = {
            "q6": q6_blocks,
            "q4": q4_blocks
        }
    return results



def find_excursion_extremes(times,cluster_sizes,n):
    crossing_indices = []

    for i in range(1,len(cluster_sizes)):
        previous_size = cluster_sizes[i-1]
        current_size = cluster_sizes[i]

        crossed_up = previous_size < n and current_size >= n
        crossed_down = previous_size > n and current_size <= n

        if crossed_up or crossed_down:
            crossing_indices.append(i)

    excursions = []

    for i in range(1, len(crossing_indices)):
        start = crossing_indices[i - 1]
        end = crossing_indices[i]
        excursion_sizes = cluster_sizes[start:end + 1]
        maximum = max(excursion_sizes)
        minimum = min(excursion_sizes)
        excursions.append((maximum, minimum))
    return excursions

def calculate_excursion_blocks(excursions):
    """
    Group excursion maximum/minimum values into blocks of 4.
    Block 1 = excursions 1-4
    Block 2 = excursions 5-8
    Block 3 = excursions 9-12
    Block 4 = excursions 13-16
    """

    block_size = 4
    blocks = []

    for block_number in range(4):

        start = block_number * block_size
        end = start + block_size

        block = excursions[start:end]

        if len(block) == block_size:

            max_values = [excursion[0] for excursion in block]
            min_values = [excursion[1] for excursion in block]

            mean_max = sum(max_values) / block_size
            mean_min = sum(min_values) / block_size

            blocks.append((mean_max, mean_min))

        else:
            blocks.append(None)

    return blocks

def process_excursion_simulation(filename, min_n, max_n):
    times, cluster_sizes = read_simulation(filename)
    results = {}
    for n in range(min_n, max_n + 1):
        excursions = find_excursion_extremes(
            times,
            cluster_sizes,
            n
        )
        print(f"\nn = {n}")
        print(f"Number of excursions: {len(excursions)}")
        print(f"First few excursions: {excursions[:5]}")

        blocks = calculate_excursion_blocks(excursions)
        print(f"Blocks: {blocks}")
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

