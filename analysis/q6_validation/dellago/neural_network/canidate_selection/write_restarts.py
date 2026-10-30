import csv
import re
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_DIR / "selected_configs.csv"
OUTPUT_DIR = SCRIPT_DIR / "starting_configs"
LAMMPS_INPUT = "in.template"
MW_FILE = "mW.sw"
DUMP_PATH_BASE = SCRIPT_DIR



def get_simulation_directory(dump_path):
    dump_file = Path(dump_path)
    if not dump_file.is_absolute():
        dump_file = DUMP_PATH_BASE / dump_file
    return dump_file.resolve().parent


def get_original_duration(input_text):
    pattern = r"(?m)^\s*variable\s+dur\s+equal\s+(\d+)\s*$"
    match = re.search(pattern, input_text)
    if not match:
        raise ValueError("Could not find 'variable dur equal ...'")
    return int(match.group(1))


def modify_input(input_text, target_timestep):
    pattern = r"(?m)^(\s*)run\s+\$\{dur\}\s*(?:#.*)?$"

    replacement = (
        f"\\g<1>run {target_timestep}\n"
        f"write_restart restart.config"
    )
    modified_text, count = re.subn(pattern,replacement,input_text)
    if count != 1:
        raise ValueError(
            f"Expected exactly one 'run ${{dur}}' command, found {count}"
        )
    return modified_text




def prepare_configs():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    with CSV_FILE.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {
            "Dump Path",
            "Frame",
            "Timestep",
            "Largest Cluster Size (n)",
            "Size Bin"
        }
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV is missing required columns: "
                f"{required_columns - set(reader.fieldnames or [])}"
            )

        for row_number, row in enumerate(reader, start=1):
            try:
                dump_path = row["Dump Path"]
                timestep = int(row["Timestep"])
                cluster_size = int(row["Largest Cluster Size (n)"])
                sim_dir = get_simulation_directory(dump_path)
                sim_name = sim_dir.name
                config_name = f"config_{row_number:03d}_{sim_name}_n{cluster_size}_t{timestep}"

                config_dir = OUTPUT_DIR / config_name
                original_input = sim_dir / LAMMPS_INPUT
                original_mW = sim_dir / MW_FILE

                if not original_input.exists():
                    raise FileNotFoundError(
                        f"Input file not found: {original_input}"
                    )

                if not original_mW.exists():
                    raise FileNotFoundError(
                        f"mW potential file not found: {original_mW}"
                    )

                input_text = original_input.read_text()
                original_duration = get_original_duration(input_text)

                modified_text = modify_input(input_text, timestep)
                config_dir.mkdir(parents=True, exist_ok=True)


                shutil.copy2(original_mW, config_dir)
                new_input = config_dir / LAMMPS_INPUT
                new_input.write_text(modified_text)

                print(f"CREATED {config_name}")
                print(f"          Source: {sim_name}")
                print(f"          Target timestep: {timestep}")
                print(f"          Output: {config_dir}")
                successful += 1

            except Exception as error:
                print(f"ERROR CSV row {row_number}: {error}")
                failed += 1

    print("\n========== SUMMARY ==========")
    print(f"Configurations created: {successful}")
    print(f"Rows failed:             {failed}")
    print(f"Output directory:        {OUTPUT_DIR}")
    print("=============================")


if __name__ == "__main__":
    prepare_configs()