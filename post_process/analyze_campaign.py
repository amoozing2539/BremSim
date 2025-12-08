import os
import glob
import re
import logging
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def parse_filename(filename):
    """
    Parses the filename to extract Energy (MeV) and Thickness.
    Expected format: output_E_{energy}MeV_T_{thickness}.root
    Example: output_E_1.0MeV_T_50um.root
    """
    basename = os.path.basename(filename)
    # Regex to capture Energy and Thickness
    # Matches: output_E_1.0MeV_T_50um.root -> 1.0, 50um
    match = re.search(r"output_E_([\d\.]+)MeV_T_(.+)\.root", basename)
    if match:
        energy = float(match.group(1))
        thickness = match.group(2)
        return energy, thickness
    return None, None

def load_data(file_path):
    """
    Loads the 'Absolute Energies' tree from the ROOT file.
    Returns a DataFrame with 'AbsEnergy' and 'ParticleID'.
    """
    try:
        with uproot.open(file_path) as file:
            if "Absolute Energies" not in file:
                logging.warning(f"Tree 'Absolute Energies' not found in {file_path}")
                return None
            
            tree = file["Absolute Energies"]
            df = tree.arrays(["AbsEnergy", "ParticleID"], library="pd")
            return df
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return None

def analyze_campaign(data_dir="."):
    """
    Scans for ROOT files, loads data, and generates summary plots.
    """
    # Find all matching ROOT files
    pattern = os.path.join(data_dir, "output_E_*_T_*.root")
    files = glob.glob(pattern)
    
    if not files:
        logging.error("No output files found matching pattern.")
        return

    logging.info(f"Found {len(files)} files. Processing...")

    # Store summary stats for Yield Plot
    # Structure: {thickness: {energy: photon_count}}
    yield_data = {}
    
    # Store full data for specific plots
    # We can't store ALL data in memory if it's 10M particles * 250 files, 
    # but we can store histograms or subsets.
    # For now, let's just store the summary yield and plot specific examples on the fly.
    
    # Define "Interesting" configurations to plot detailed spectra for
    # Example: Plot spectra for all thicknesses at Max Energy
    # Example: Plot spectra for all energies at a specific Thickness
    
    # First pass: Collect metadata and calculate yields
    file_metadata = []
    for f in files:
        energy, thickness = parse_filename(f)
        if energy is None:
            continue
            
        file_metadata.append({
            "path": f,
            "energy": energy,
            "thickness": thickness
        })

    # Convert to DataFrame for easier filtering
    meta_df = pd.DataFrame(file_metadata)
    
    if meta_df.empty:
        logging.error("No valid metadata extracted from filenames.")
        return

    unique_energies = sorted(meta_df["energy"].unique())
    unique_thicknesses = sorted(meta_df["thickness"].unique(), key=lambda x: (float(re.findall(r"[\d\.]+", x)[0]) if re.findall(r"[\d\.]+", x) else 0))

    logging.info(f"Energies: {unique_energies}")
    logging.info(f"Thicknesses: {unique_thicknesses}")

    # --- PLOT 1: Total Photon Yield vs Energy (for each Thickness) ---
    plt.figure(figsize=(10, 6))
    
    for thick in unique_thicknesses:
        subset = meta_df[meta_df["thickness"] == thick].sort_values("energy")
        energies = []
        yields = []
        
        for _, row in subset.iterrows():
            df = load_data(row["path"])
            if df is not None:
                # Count photons (ParticleID == 0)
                photon_count = len(df[df["ParticleID"] == 0])
                energies.append(row["energy"])
                yields.append(photon_count)
        
        if energies:
            plt.plot(energies, yields, marker='o', label=thick)

    plt.title("Total Photon Yield vs Beam Energy")
    plt.xlabel("Electron Beam Energy (MeV)")
    plt.ylabel("Total Photons Detected")
    plt.legend(title="Foil Thickness")
    plt.grid(True, alpha=0.3)
    plt.savefig("total_yield_vs_energy.png")
    logging.info("Saved total_yield_vs_energy.png")


    # --- PLOT 2: Spectra Comparison (Fixed Energy, Varying Thickness) ---
    # Pick the highest energy available to see the most features
    target_energy = unique_energies[-1] 
    logging.info(f"Plotting spectra for fixed Energy: {target_energy} MeV")
    
    plt.figure(figsize=(10, 6))
    subset = meta_df[meta_df["energy"] == target_energy]
    
    for _, row in subset.iterrows():
        df = load_data(row["path"])
        if df is not None:
            photons = df[df["ParticleID"] == 0]["AbsEnergy"]
            # Use fixed bins for comparison
            plt.hist(photons, bins=100, range=(0, target_energy), histtype='step', linewidth=2, label=row["thickness"], density=True)

    plt.title(f"Photon Spectra at {target_energy} MeV Beam Energy")
    plt.xlabel("Photon Energy (MeV)")
    plt.ylabel("Normalized Count")
    plt.yscale('log')
    plt.legend(title="Foil Thickness")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"spectra_E_{target_energy}MeV_comparison.png")
    logging.info(f"Saved spectra_E_{target_energy}MeV_comparison.png")


    # --- PLOT 3: Spectra Evolution (Fixed Thickness, Varying Energy) ---
    # Pick a middle thickness
    target_thickness = unique_thicknesses[len(unique_thicknesses)//2]
    logging.info(f"Plotting spectra for fixed Thickness: {target_thickness}")
    
    plt.figure(figsize=(10, 6))
    subset = meta_df[meta_df["thickness"] == target_thickness].sort_values("energy")
    
    # Plot a few selected energies to avoid clutter (e.g., 5 steps)
    step = max(1, len(subset) // 5)
    selected_rows = subset.iloc[::step]
    
    for _, row in selected_rows.iterrows():
        df = load_data(row["path"])
        if df is not None:
            photons = df[df["ParticleID"] == 0]["AbsEnergy"]
            plt.hist(photons, bins=100, histtype='step', linewidth=2, label=f"{row['energy']} MeV")

    plt.title(f"Photon Spectra Evolution for {target_thickness} Foil")
    plt.xlabel("Photon Energy (MeV)")
    plt.ylabel("Count")
    plt.yscale('log')
    plt.legend(title="Beam Energy")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"spectra_T_{target_thickness}_evolution.png")
    logging.info(f"Saved spectra_T_{target_thickness}_evolution.png")

if __name__ == "__main__":
    # Run in the current directory where the root files are
    analyze_campaign(".")
