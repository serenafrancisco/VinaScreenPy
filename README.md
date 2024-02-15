# VinaScreenPy

Virtual screening of compounds using AutoDock Vina v1.2.3 (https://github.com/ccsb-scripps/AutoDock-Vina/releases).

## Description
The present script takes one ligand file at a time (in PDBQT format) from a specified folder and generates a *_output.log and a *_out.PDBQT file in separate folders. Finally, a merged log file is written and manipulated to generate a simplified CSV file with Vina results, as well as a TXT file containing molecules that gave errors during docking. 

Check the DrugTagger repository at https://github.com/serenafrancisco/DrugTagger for a faster annotation of docking results.
