import os
import re

def read_and_write_dump(filename, output_file, written_timesteps):
    frames_written = 0
    duplicates_skipped = 0
    with open(filename, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.strip() != "ITEM: TIMESTEP":
                continue
            timestep_line = f.readline()
            if not timestep_line:
                break
            timestep = int(timestep_line.strip())
            line = f.readline()
            if not line:
                raise RuntimeError(
                    f"Incomplete frame at timestep {timestep} "
                    f"in {filename}"
                )
            num_atoms_line = f.readline()
            if not num_atoms_line:
                raise RuntimeError(
                    f"Incomplete frame at timestep {timestep} "
                    f"in {filename}"
                )
            num_atoms = int(num_atoms_line.strip())

            box_header = f.readline()
            if not box_header:
                raise RuntimeError(
                    f"Incomplete frame at timestep {timestep} "
                    f"in {filename}"
                )
            box_lines = []
            for _ in range(3):
                line = f.readline()
                if not line:
                    raise RuntimeError(
                        f"Incomplete frame at timestep {timestep} "
                        f"in {filename}"
                    )
                box_lines.append(line)
            atoms_header = f.readline()
            if not atoms_header:
                raise RuntimeError(
                    f"Incomplete frame at timestep {timestep} "
                    f"in {filename}"
                )
            atom_lines = []
            for _ in range(num_atoms):
                line = f.readline()
                if not line:
                    raise RuntimeError(
                        f"Incomplete frame at timestep {timestep} "
                        f"in {filename}"
                    )
                atom_lines.append(line)

            if timestep in written_timesteps:
                duplicates_skipped += 1
                print(
                    f"    Duplicate timestep {timestep} "
                    f"-- skipping"
                )
                continue
            written_timesteps.add(timestep)
            # Write directly to output file
            output_file.write("ITEM: TIMESTEP\n")
            output_file.write(f"{timestep}\n")
            output_file.write(line_header := "ITEM: NUMBER OF ATOMS\n")
            output_file.write(f"{num_atoms}\n")
            output_file.write(box_header)
            for box_line in box_lines:
                output_file.write(box_line)
            output_file.write(atoms_header)
            for atom_line in atom_lines:
                output_file.write(atom_line)
            frames_written += 1
    return frames_written, duplicates_skipped


def find_dump_files(dump_directory):
    dump_files = []
    pattern = re.compile(r"dump\.(\d+)\.lammpstrj$")
    for filename in os.listdir(dump_directory):
        match = pattern.match(filename)
        if match:
            cycle = int(match.group(1))
            dump_files.append(
                (cycle, os.path.join(dump_directory, filename))
            )
    dump_files.sort(key=lambda x: x[0])
    return dump_files


def concatenate_dumps(dump_directory, output_filename):
    dump_files = find_dump_files(dump_directory)
    if not dump_files:
        raise RuntimeError(
            f"No dump.N.lammpstrj files found in {dump_directory}"
        )

    written_timesteps = set()
    total_frames = 0
    total_duplicates = 0
    print("Dump files found:")
    for cycle, filename in dump_files:
        print(f"  Cycle {cycle}: {filename}")
    print()
    print("Creating combined dump...")
    with open(output_filename, "w") as output_file:
        for cycle, filename in dump_files:
            print(f"\nProcessing cycle {cycle}...")
            frames_written, duplicates_skipped = (
                read_and_write_dump(
                    filename,
                    output_file,
                    written_timesteps
                )
            )
            total_frames += frames_written
            total_duplicates += duplicates_skipped
            print(f"Frames written: {frames_written}")
            print(f"Duplicates skipped: {duplicates_skipped}")
    print()
    print("--------------------------------")
    print("Concatenation complete")
    print("--------------------------------")
    print(f"Total frames written: {total_frames}")
    print(f"Duplicate frames skipped: {total_duplicates}")
    print(f"Unique timesteps: {len(written_timesteps)}")
    print(f"Output file: {output_filename}")


def delete_individual_dumps(dump_directory="dumps"):
    pattern = re.compile(r"dump\.\d+\.lammpstrj$")
    deleted = 0
    total_size = 0
    for filename in os.listdir(dump_directory):
        if pattern.match(filename):
            filepath = os.path.join(dump_directory, filename)
            file_size = os.path.getsize(filepath)
            total_size += file_size
            os.remove(filepath)
            deleted += 1
            print(f"Deleted: {filepath}")

    print()
    print("--------------------------------")
    print("Dump cleanup complete")
    print("--------------------------------")
    print(f"Files deleted: {deleted}")
    print(f"Space freed: {total_size / (1024**3):.2f} GB")



if __name__ == "__main__":
    dump_directory = "dumps"
    output_filename = "dumps/dump.combined.lammpstrj"
    concatenate_dumps(
        dump_directory,
        output_filename
    )
    delete_individual_dumps()