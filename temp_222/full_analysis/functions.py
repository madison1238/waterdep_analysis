import csv


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