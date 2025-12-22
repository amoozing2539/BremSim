import os
import glob
import re
import logging
import argparse
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def freedman_diaconis(data):
    """
    Calculate optimal bin width using Freedman-Diaconis rule.
    Bin Width = 2 * IQR * n^(-1/3)
    """
    if len(data) < 2:
        return 0.1
    # Check for zero range
    if data.max() == data.min():
        return 0.1
        
    q75, q25 = np.percentile(data, [75 ,25])
    iqr = q75 - q25
    n = len(data)
    
    if iqr == 0:
        # Fallback if IQR is 0 (e.g. all data is same or very concentrated)
        # Use std dev based rule or simple fixed count
        std = np.std(data)
        if std == 0:
            return 0.1
        bin_width = 3.5 * std * (n ** (-1/3))
        return bin_width
        
    bin_width = 2 * iqr * (n ** (-1/3))
    return bin_width

def process_file(file_path):
    """
    Processes a single ROOT file and generates a spectrum plot.
    """
    try:
        with uproot.open(file_path) as file:
            tree_name = "Absolute Energies"
            if tree_name not in file:
                logging.warning(f"Tree '{tree_name}' not found in {file_path}")
                return

            df = file[tree_name].arrays(["AbsEnergy", "ParticleID"], library="pd")
            
            if df.empty:
                logging.warning(f"No data in {file_path}")
                return

            # Plotting
            plt.figure(figsize=(10, 6))
            
            # Particle Types provided by Geant4 simulation
            particles = {
                0: {"name": "Photons", "color": "blue"},
                1: {"name": "Electrons", "color": "red"},
                2: {"name": "Positrons", "color": "green"}
            }

            has_data = False
            for pid, info in particles.items():
                subset = df[df["ParticleID"] == pid]["AbsEnergy"]
                if not subset.empty:
                    # Calculate bins using Freedman-Diaconis
                    bw = freedman_diaconis(subset)
                    if bw > 0:
                        bins = int((subset.max() - subset.min()) / bw)
                        bins = max(10, min(bins, 200)) # Safety Limits
                    else:
                        bins = 100

                    plt.hist(subset, bins=bins, log=True, histtype='step', linewidth=2, 
                             label=info["name"], color=info["color"])
                    has_data = True
            
            if has_data:
                plt.title(f"Particle Spectra\n{os.path.basename(file_path)}")
                plt.xlabel("Energy (MeV)")
                plt.ylabel("Counts")
                plt.legend()
                plt.grid(True, which="both", ls="--", alpha=0.5)
                
                # Save plot
                output_path = os.path.splitext(file_path)[0] + "_spectra.png"
                plt.savefig(output_path)
                plt.close()
                logging.info(f"Saved plot: {output_path}")
            else:
                plt.close()
                logging.info(f"No relevant particles found in {os.path.basename(file_path)}")

    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")

def analyze_campaign(data_dir):
    """
    Scans for ROOT files and generates plots for each.
    """
    # Find all ROOT files recursively or just in the top level? 
    pattern = os.path.join(data_dir, "*.root")
    files = glob.glob(pattern)
    
    if not files:
        logging.warning(f"No .root files found in {data_dir}")
        return

    logging.info(f"Found {len(files)} ROOT files in {data_dir}. Processing...")
    
    for f in files:
        process_file(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze BremSim ROOT files.")
    parser.add_argument("data_dir", nargs="?", default=None, help="Directory containing ROOT files")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target directory logic
    if args.data_dir:
        target_dir = args.data_dir
    else:
        # Default to 'post_process/non_trained' if it exists, else current dir
        default_target = os.path.join(script_dir, "non_trained")
        if os.path.exists(default_target):
            target_dir = default_target
        else:
            target_dir = "."

    if os.path.exists(target_dir):
        analyze_campaign(target_dir)
    else:
        logging.error(f"Target directory does not exist: {target_dir}")
