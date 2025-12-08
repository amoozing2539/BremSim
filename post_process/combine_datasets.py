import os
import glob
import re
import logging
import uproot
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def parse_filename(filename):
    """
    Parses the filename to extract Energy (MeV) and Thickness.
    Returns Energy (float) and Thickness (float in microns).
    """
    basename = os.path.basename(filename)
    match = re.search(r"output_E_([\d\.]+)MeV_T_(.+)\.root", basename)
    if match:
        energy = float(match.group(1))
        thick_str = match.group(2)
        
        # Convert thickness to microns
        if "mm" in thick_str:
            thickness = float(re.findall(r"[\d\.]+", thick_str)[0]) * 1000
        elif "um" in thick_str:
            thickness = float(re.findall(r"[\d\.]+", thick_str)[0])
        else:
            thickness = 0.0 # Should not happen based on filename format
            
        return energy, thickness
    return None, None

def freedman_diaconis(data):
    """
    Calculate optimal bin width using Freedman-Diaconis rule.
    """
    if len(data) < 2:
        return 0.1
    q75, q25 = np.percentile(data, [75 ,25])
    iqr = q75 - q25
    n = len(data)
    if iqr == 0:
        return 0.1
    bin_width = 2 * iqr * (n ** (-1/3))
    return bin_width

def combine_data(data_dir="."):
    logging.info("Starting data combination process...")

    # 1. Determine Global Binning Scheme
    # We use the 5.0 MeV configuration (max energy) to determine a bin width 
    # that captures the necessary detail for the largest range.
    ref_pattern = os.path.join(data_dir, "output_E_5.0MeV_T_1mm.root")
    ref_files = glob.glob(ref_pattern)
    
    if not ref_files:
        # Fallback if specific file not found, try any 5.0MeV
        ref_files = glob.glob(os.path.join(data_dir, "output_E_5.0MeV_*.root"))
        if not ref_files:
            logging.error("Could not find reference 5.0 MeV file for binning calculation.")
            return

    ref_file = ref_files[0]
    logging.info(f"Using reference file for bin width calculation: {ref_file}")
    
    try:
        with uproot.open(ref_file) as file:
            df_ref = file["Absolute Energies"].arrays(["AbsEnergy", "ParticleID"], library="pd")
            # Use photons for the 'primary' bin width as they are the main interest usually
            # But we can check both or just use the whole set. 
            # Photons often have a sharp characteristic X-ray peak so they might demand smaller bins.
            ref_data = df_ref[df_ref["ParticleID"] == 0]["AbsEnergy"]
            
            bin_width = freedman_diaconis(ref_data)
            logging.info(f"Calculated Freedman-Diaconis Bin Width: {bin_width:.5f} MeV")
            
    except Exception as e:
        logging.error(f"Failed to calculate bin width: {e}")
        return

    # Define Global Bins
    max_energy = 5.05 # Slightly above 5.0
    bins = np.arange(0, max_energy + bin_width, bin_width)
    logging.info(f"Global Bins defined: {len(bins)-1} bins from 0 to {bins[-1]:.2f} MeV")

    # 2. Process All Files
    files = glob.glob(os.path.join(data_dir, "output_E_*_T_*.root"))
    
    data_rows = []
    
    # Store bin centers for column names maybe? 
    # Or just store the counts and metadata.
    # Let's create a list of dicts.
    
    logging.info(f"Processing {len(files)} files...")
    
    for i, f in enumerate(files):
        if i % 20 == 0:
            logging.info(f"Processed {i}/{len(files)} files...")
            
        energy, thickness = parse_filename(f)
        if energy is None:
            continue
            
        try:
            with uproot.open(f) as file:
                if "Absolute Energies" not in file:
                    continue
                df = file["Absolute Energies"].arrays(["AbsEnergy", "ParticleID"], library="pd")
                
                # Separate particles
                photons = df[df["ParticleID"] == 0]["AbsEnergy"]
                electrons = df[df["ParticleID"] == 1]["AbsEnergy"]
                
                # Histogram
                p_counts, _ = np.histogram(photons, bins=bins)
                e_counts, _ = np.histogram(electrons, bins=bins)
                
                # Create Row
                row = {
                    "Energy_MeV": energy,
                    "Thickness_um": thickness,
                    "Total_Photons": len(photons),
                    "Total_Electrons": len(electrons)
                }
                
                # Add spectral data
                # We can store as array columns or flattened. 
                # For a "single data table" csv style, flattened is best.
                # For PKL/Parquet, array columns are cleaner.
                # Given "combine all... single data table", array columns are likely more manageable 
                # than 2000 columns of integers.
                
                row["Photon_Spectrum"] = p_counts
                row["Electron_Spectrum"] = e_counts
                
                data_rows.append(row)
                
        except Exception as e:
            logging.warning(f"Error processing {f}: {e}")

    # 3. Create DataFrame
    df_final = pd.DataFrame(data_rows)
    
    # Sort
    df_final = df_final.sort_values(by=["Thickness_um", "Energy_MeV"]).reset_index(drop=True)
    
    # Save
    pkl_path = "combined_spectra_table.pkl"
    df_final.to_pickle(pkl_path)
    logging.info(f"Saved combined data table to {os.path.abspath(pkl_path)}")
    
    # Also save bin edges for reference
    np.save("bin_edges.npy", bins)
    logging.info("Saved bin_edges.npy")

    # Quick peek
    print(df_final.head())
    print(f"Shape: {df_final.shape}")

if __name__ == "__main__":
    combine_data(".")
