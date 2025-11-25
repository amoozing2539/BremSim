import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def freedman_diaconis(data):
    """
    Calculate optimal bin width using Freedman-Diaconis rule.
    Bin Width = 2 * IQR * n^(-1/3)
    """
    q75, q25 = np.percentile(data, [75 ,25])
    iqr = q75 - q25
    n = len(data)
    if iqr == 0:
        return 0.1 # Fallback
    bin_width = 2 * iqr * (n ** (-1/3))
    return bin_width

def calculate_bins():
    # Path to the PKL file
    # Assuming it's in the build/Release folder based on previous steps
    pkl_path = os.path.join("..", "build", "Release", "output_dataset.pkl")
    
    if not os.path.exists(pkl_path):
        logging.error("PKL file not found: %s", pkl_path)
        return

    logging.info("Loading data from: %s", pkl_path)
    df = pd.read_pickle(pkl_path)
    
    if "ParticleID" not in df.columns or "AbsEnergy" not in df.columns:
        logging.error("Required columns not found in DataFrame.")
        return

    # Separate data
    photons = df[df["ParticleID"] == 0]["AbsEnergy"]
    electrons = df[df["ParticleID"] == 1]["AbsEnergy"]
    
    logging.info("Photons: %d, Electrons: %d", len(photons), len(electrons))

    # Calculate bins for Photons
    if len(photons) > 0:
        bw_gamma = freedman_diaconis(photons)
        bins_gamma = int((photons.max() - photons.min()) / bw_gamma)
        logging.info("Photons - Optimal Bin Width: %.4f MeV, Number of Bins: %d", bw_gamma, bins_gamma)
    else:
        bins_gamma = 100
        logging.warning("No photons found.")

    # Calculate bins for Electrons
    if len(electrons) > 0:
        bw_e = freedman_diaconis(electrons)
        bins_e = int((electrons.max() - electrons.min()) / bw_e)
        logging.info("Electrons - Optimal Bin Width: %.4f MeV, Number of Bins: %d", bw_e, bins_e)
    else:
        bins_e = 100
        logging.warning("No electrons found.")

    # Plot with optimal bins
    plt.figure(figsize=(10, 6))
    
    if len(photons) > 0:
        plt.hist(photons, bins=bins_gamma, log=True, histtype='stepfilled', alpha=0.5, label=f'Photons (bins={bins_gamma})', color='blue')
    
    if len(electrons) > 0:
        plt.hist(electrons, bins=bins_e, log=True, histtype='stepfilled', alpha=0.5, label=f'Electrons (bins={bins_e})', color='red')
        
    plt.title("Particle Energy Spectrum (Optimal Bins)")
    plt.xlabel("Energy (MeV)")
    plt.ylabel("Counts")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    plot_path = "optimal_bins_spectrum.png"
    plt.savefig(plot_path)
    logging.info("Saved plot to: %s", os.path.abspath(plot_path))

if __name__ == "__main__":
    calculate_bins()
