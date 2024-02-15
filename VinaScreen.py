################################### VIRTUAL SCREENING WITH AUTODOCK VINA 1.2.3 ###################################

import subprocess
import glob
import os

vina_executable = "vina"
logs_folder = "./logs"
ligand_folder = "./ligands"
output_folder = "./VS_results"

# Get a list of ligand files in the folder
ligand_files = glob.glob(f"{ligand_folder}/*.pdbqt")

# Create the logs and output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(logs_folder, exist_ok=True)

# Process each ligand individually
for ligand_file in ligand_files:
    print(f"Processing ligand: {ligand_file}")

    # Extract ligand name without extension
    ligand_name = os.path.splitext(os.path.basename(ligand_file))[0]

    # Example command with input parameters
    command = f"{vina_executable} --config conf.txt --batch {ligand_file}"

    # Run AutoDock Vina using subprocess
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Write stdout and stderr to a log file
    log_file_path = os.path.join(logs_folder, f"{ligand_name}_output.log")
    with open(log_file_path, "w") as log_file:
        log_file.write(result.stdout)
        log_file.write("\n")
        log_file.write(result.stderr)

    # Print the output to see if there are any errors
    print(result.stdout)

    # Check the return code to see if the command was successful
    if result.returncode == 0:
        print("AutoDock Vina executed successfully.")
    else:
        print(f"Error: AutoDock Vina exited with code {result.returncode}")
        print(f"Error for ligand {ligand_file}. Check the log file: {log_file_path}")
################################### RESULTS MANIPULATION ###################################

comb_log = "./comb_log.txt"

# Get a list of all log files in the logs folder
log_files = [f for f in os.listdir(logs_folder) if f.endswith("_output.log")]


# Sort the log files to maintain order
log_files.sort()

# Open the combined log file for appending
with open(comb_log, "a") as combined_log:
    # Iterate through each individual log file and append its content to the combined log
    for log_file in log_files:
        log_file_path = os.path.join(logs_folder, log_file)
        with open(log_file_path, "r") as individual_log:
            # Add a separator between logs for different ligands
            combined_log.write(f"### Results for {log_file[:-11]} ###\n")
            combined_log.write(individual_log.read())
            combined_log.write("\n")
################################### EXTRACT AFFINITY OF MODE 1 FOR EACH COMPOUND ###################################

import re
import csv

def extract_affinity(file_content, drug_id, csv_writer, error_writer):
    # Define a regex pattern to match the affinity line
    pattern = re.compile(r'\s+(\d+)\s+(-?\d+\.\d+)\s+\d+\s+\d+')

    # Check for PDBQT parsing error
    pdbqt_error = any("PDBQT parsing error" in line for line in file_content)

    # Write the results to CSV or error file based on the presence of errors
    if not pdbqt_error:
        # Iterate through lines in the file content
        for line in file_content:
            # Check if the line matches the pattern
            match = pattern.match(line)
            if match:
                # Extract mode and affinity value
                mode = match.group(1)
                affinity_value = float(match.group(2))

                # Write the results to CSV
                csv_writer.writerow([drug_id, mode, affinity_value])
    else:
        # Write the error results to the error file
        error_writer.write(f"{drug_id}: no results available\n")

# Open CSV file for results and error file for error molecules
csv_filename = "vina_results.csv"
error_filename = "vina_errors.txt"

with open(csv_filename, "w", newline="") as csv_file, open(error_filename, "w") as error_file:
    csv_writer = csv.writer(csv_file)

    # Write the header only once
    csv_writer.writerow(["ID", "Mode", "Affinity"])

    # Read the text file
    with open("comb_log.txt", "r") as file:
        compound_blocks = file.read().split("### Results for ")

        # Process each compound block
        for block in compound_blocks[1:]:
            # Split the block into lines
            block_lines = block.split('\n')

            # Extract Drug ID
            drug_id_match = re.search(r'DB\d+', block_lines[0])
            drug_id = drug_id_match.group() if drug_id_match else None

            # Extract affinity value for the compound
            if drug_id:
                extract_affinity(block_lines, drug_id, csv_writer, error_file)

print(f"Results saved to {csv_filename}")
print(f"Error molecules saved to {error_filename}")