
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

#settings
input_csv = Path("all_candidates.csv")
output_csv = Path("selected_configs.csv")
total_needed_configs = 270
configs_per_bin = 54
max_per_dump = 2
min_frame_seperation = 100
random_seed = 42
print(f"Seed: {random_seed}")
max_attempts = 100
size_bins = ["10-19", "20-29", "30-39", "40-49", "50-60"]



with input_csv.open("r", newline="") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    candidates = list(reader)

required_columns = {
    "Dump Path",
    "Frame",
    "Timestep",
    "Largest Cluster Size (n)",
    "Size Bin",
}

if not fieldnames or not required_columns.issubset(fieldnames):
    raise ValueError(
        f"Input CSV must contain these columns: {sorted(required_columns)}\n"
        f"Found: {fieldnames}"
    )

candidates_by_bin = defaultdict(list)

for row in candidates:
    row["Frame"] = int(row["Frame"])
    row["Timestep"] = int(row["Timestep"])
    row["Largest Cluster Size (n)"] = int(row["Largest Cluster Size (n)"])

    if row["Size Bin"] not in size_bins:
        raise ValueError(f"Unexpected size bin: {row['Size Bin']}")

    candidates_by_bin[row["Size Bin"]].append(row)

print(f"Loaded {len(candidates)} candidate frames.")
print("\nAvailable candidates per bin:")
for size_bin in size_bins:
    bin_candidates = candidates_by_bin[size_bin]
    distinct_dumps = len({r["Dump Path"] for r in bin_candidates})
    print(
        f"{size_bin}: {len(bin_candidates):,} frames "
        f"across {distinct_dumps} dumps"
    )

minimum_dumps_per_bin = (configs_per_bin + max_per_dump - 1) // max_per_dump

for size_bin in size_bins:
    distinct_dumps = len({r["Dump Path"] for r in candidates_by_bin[size_bin]})
    if len(candidates_by_bin[size_bin]) < configs_per_bin:
        raise RuntimeError(
            f"Not enough candidates in bin {size_bin}."
        )
    if distinct_dumps < minimum_dumps_per_bin:
        raise RuntimeError(
            f"Bin {size_bin} appears infeasible: only "
            f"{distinct_dumps} distinct dumps, but at least "
            f"{minimum_dumps_per_bin} are needed."
        )



def try_selection(seed):
    rng = random.Random(seed)
    bin_order = size_bins.copy()
    rng.shuffle(bin_order)
    selected = []
    selected_per_bin = Counter()
    selected_per_dump = defaultdict(list)


    shuffled_candidates = {}
    for size_bin in size_bins:
        pool = candidates_by_bin[size_bin].copy()
        rng.shuffle(pool)
        shuffled_candidates[size_bin] = pool

    for size_bin in bin_order:
        for row in shuffled_candidates[size_bin]:
            if selected_per_bin[size_bin] >= configs_per_bin:
                break
            dump_path = row["Dump Path"]
            frame = row["Frame"]

            if len(selected_per_dump[dump_path]) >= max_per_dump:
                continue

            existing_frames = selected_per_dump[dump_path]
            if any(abs(frame - previous_frame) < min_frame_seperation for previous_frame in existing_frames):
                continue

            selected.append(row)
            selected_per_bin[size_bin] += 1
            selected_per_dump[dump_path].append(frame)

    if (
        len(selected) == total_needed_configs
        and all(selected_per_bin[size_bin] == configs_per_bin for size_bin in size_bins)):
        return selected
    return None

selected = None
for attempt in range(max_attempts):
    selected = try_selection(random_seed + attempt)
    if selected is not None:
        print(f"\nSuccessful selection on attempt {attempt + 1}.")
        break

if selected is None:
    raise RuntimeError(
        f"Could not find a valid selection after {max_attempts} "
        "attempts. No output file was written."
    )

selected.sort(
    key=lambda row: (
        row["Size Bin"],
        row["Dump Path"],
        row["Frame"],
    )
)


with output_csv.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(selected)

bin_counts = Counter(row["Size Bin"] for row in selected)
dump_counts = Counter(row["Dump Path"] for row in selected)

print(f"\nSaved {len(selected)} configurations to {output_csv}")
print("\nSelected configurations per bin:")
for size_bin in size_bins:
    print(f"  {size_bin}: {bin_counts[size_bin]}")
print(f"\nDistinct dump files used: {len(dump_counts)}")
print(f"Maximum selected from any dump: {max(dump_counts.values())}")
print("\nSelection complete! :D")