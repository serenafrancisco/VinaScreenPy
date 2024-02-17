################################### VIRTUAL SCREENING WITH AUTODOCK VINA 1.2.3 ###################################

import subprocess
import glob
import os
import re
import csv

vina_executable = "vina"
ligands_folder = "./ligands"
logs_folder = "./logs"
output_folder = "./VS_results"

ligand_files = glob.glob(f"{ligands_folder}/*.pdbqt")

os.makedirs(logs_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)


for ligand_file in ligand_files:
    print(f"Processing ligand: {ligand_file}")

    ligand_name = os.path.splitext(os.path.basename(ligand_file))[0]
    command = f"{vina_executable} --config conf.txt --batch {ligand_file}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    log_file_path = os.path.join(logs_folder, f"{ligand_name}_output.log")
    with open(log_file_path, "w") as log_file:
        log_file.write(result.stdout)
        log_file.write("\n")
        log_file.write(result.stderr)

    print(result.stdout)

    if result.returncode == 0:
        print("AutoDock Vina executed successfully.")
    else:
        print(f"Error: AutoDock Vina exited with code {result.returncode}")
        print(f"Error for ligand {ligand_file}. Check the log file: {log_file_path}")

################################### RESULTS MANIPULATION ###################################

comb_log = "./comb_log.txt"

log_files = [f for f in os.listdir(logs_folder) if f.endswith("_output.log")]
log_files.sort()

with open(comb_log, "a") as combined_log:
    for log_file in log_files:
        log_file_path = os.path.join(logs_folder, log_file)
        with open(log_file_path, "r") as individual_log:
            combined_log.write(f"### Results for {log_file[:-11]} ###\n")
            combined_log.write(individual_log.read())
            combined_log.write("\n")

################################### EXTRACT AFFINITY OF MODE 1 FOR EACH COMPOUND ###################################

def extract_affinity(file_content, drug_id, csv_writer, error_writer):
    pattern = re.compile(r'\s+(\d+)\s+(-?\d+\.\d+)\s+\d+\s+\d+')
    pdbqt_error = any("PDBQT parsing error" in line for line in file_content)
    if not pdbqt_error:
        for line in file_content:
            match = pattern.match(line)
            if match:
                mode = match.group(1)
                affinity_value = float(match.group(2))
                csv_writer.writerow([drug_id, mode, affinity_value])
    else:
        error_writer.write(f"{drug_id}: no results available\n")

csv_filename = "vina_results.csv"
error_filename = "vina_errors.txt"

with open(csv_filename, "w", newline="") as csv_file, open(error_filename, "w") as error_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["ID", "Mode", "Affinity"])
    with open("comb_log.txt", "r") as file:
        compound_blocks = file.read().split("### Results for ")

        for block in compound_blocks[1:]:
            block_lines = block.split('\n')
            drug_id_match = re.search(r'DB\d+', block_lines[0])
            drug_id = drug_id_match.group() if drug_id_match else None
            
            if drug_id:
                extract_affinity(block_lines, drug_id, csv_writer, error_file)

print(f"Results saved to {csv_filename}")
print(f"Error molecules saved to {error_filename}")