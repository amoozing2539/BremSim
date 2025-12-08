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

    # First pass: Collect metadata
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
    # Sort thicknesses roughly by value
    def parse_thick(s):
        val = float(re.findall(r"[\d\.]+", s)[0])
        if "mm" in s: val *= 1000
        return val
        
    unique_thicknesses = sorted(meta_df["thickness"].unique(), key=parse_thick)

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
    # Pick the highest energy available
    target_energy = unique_energies[-1] 
    logging.info(f"Plotting spectra for fixed Energy: {target_energy} MeV")
    
    plt.figure(figsize=(12, 7))
    subset = meta_df[meta_df["energy"] == target_energy]
    
    for _, row in subset.iterrows():
        df = load_data(row["path"])
        if df is not None:
            # Photons (ID 0)
            photons = df[df["ParticleID"] == 0]["AbsEnergy"]
            # Electrons (ID 1)
            electrons = df[df["ParticleID"] == 1]["AbsEnergy"]
            
            # Label
            lbl = row["thickness"]
            
            # Plot Photons
            if len(photons) > 0:
                bw_p = freedman_diaconis(photons)
                bins_p = int((photons.max() - photons.min()) / bw_p)
                bins_p = max(10, min(bins_p, 200)) # Safety Limits
                plt.hist(photons, bins=bins_p, histtype='step', linewidth=2, label=f"{lbl} $\gamma$", density=True)
            
            # Plot Electrons
            if len(electrons) > 0:
                bw_e = freedman_diaconis(electrons)
                bins_e = int((electrons.max() - electrons.min()) / bw_e)
                bins_e = max(10, min(bins_e, 200)) # Safety Limits
                plt.hist(electrons, bins=bins_e, histtype='step', linewidth=2, linestyle='--', label=f"{lbl} $e^-$", density=True)

    plt.title(f"Particle Spectra at {target_energy} MeV Beam Energy")
    plt.xlabel("Energy (MeV)")
    plt.ylabel("Normalized Count")
    plt.yscale('log')
    plt.legend(title="Foil Thickness / Particle")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"spectra_E_{target_energy}MeV_comparison.png")
    logging.info(f"Saved spectra_E_{target_energy}MeV_comparison.png")


    # --- PLOT 3: Spectra Evolution (Fixed Thickness, Varying Energy) ---
    target_thickness = unique_thicknesses[len(unique_thicknesses)//2]
    logging.info(f"Plotting spectra for fixed Thickness: {target_thickness}")
    
    plt.figure(figsize=(12, 7))
    subset = meta_df[meta_df["thickness"] == target_thickness].sort_values("energy")
    
    # Plot a few selected energies
    step = max(1, len(subset) // 5)
    selected_rows = subset.iloc[::step]
    
    for _, row in selected_rows.iterrows():
        df = load_data(row["path"])
        if df is not None:
            photons = df[df["ParticleID"] == 0]["AbsEnergy"]
            electrons = df[df["ParticleID"] == 1]["AbsEnergy"]
            
            lbl = f"{row['energy']} MeV"
            
            if len(photons) > 0:
                bw_p = freedman_diaconis(photons)
                bins_p = int((photons.max() - photons.min()) / bw_p)
                bins_p = max(10, min(bins_p, 200)) # Safety Limits
                plt.hist(photons, bins=bins_p, histtype='step', linewidth=2, label=f"{lbl} $\gamma$")
                
            if len(electrons) > 0:
                bw_e = freedman_diaconis(electrons)
                bins_e = int((electrons.max() - electrons.min()) / bw_e)
                bins_e = max(10, min(bins_e, 200)) # Safety Limits
                plt.hist(electrons, bins=bins_e, histtype='step', linewidth=2, linestyle='--', label=f"{lbl} $e^-$")

    plt.title(f"Particle Spectra Evolution for {target_thickness} Foil")
    plt.xlabel("Energy (MeV)")
    plt.ylabel("Count")
    plt.yscale('log')
    plt.legend(title="Beam Energy / Particle")
    plt.grid(True, alpha=0.3)
    plt.savefig(f"spectra_T_{target_thickness}_evolution.png")
    logging.info(f"Saved spectra_T_{target_thickness}_evolution.png")

if __name__ == "__main__":
    analyze_campaign(".")
