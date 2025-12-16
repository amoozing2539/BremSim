import os
import glob
import re
import pickle
import numpy as np
import pandas as pd
import uproot

def parse_filename(filename):
    """
    Parses the filename to extract Energy (MeV) and Thickness.
    Expected format: output_E_{energy}MeV_T_{thickness}.root
    Example: output_E_1.0MeV_T_50um.root
    """
    basename = os.path.basename(filename)
    # This regex needs to be robust to "T_250um" vs "T_1.5mm"
    # Matches: ..._T_{value}{unit}.root
    match = re.search(r"output_E_([\d\.]+)MeV_T_([\d\.]+)(\w+)\.root", basename)
    
    if match:
        energy = float(match.group(1))
        thick_val = float(match.group(2))
        thick_unit = match.group(3)
        
        # Convert all to um
        if thick_unit == "mm":
            thickness = thick_val * 1000.0
        elif thick_unit == "um":
            thickness = thick_val
        else:
            print(f"Unknown unit {thick_unit} in {basename}")
            return None, None
            
        return energy, thickness
    return None, None

def process_data(data_dir, bin_edges_path, output_pkl):
    print(f"Processing ROOT files in {data_dir}...")
    
    # Load bin edges
    bin_edges = np.load(bin_edges_path)
    
    # Storage
    records = []
    
    root_files = glob.glob(os.path.join(data_dir, "*.root"))
    print(f"Found {len(root_files)} ROOT files.")
    
    for root_file in root_files:
        energy, thickness = parse_filename(root_file)
        if energy is None:
            continue
            
        try:
            with uproot.open(root_file) as file:
                # Assuming tree name is 'BremSim' or similar based on previous context, 
                # but analyze_campaign.py didn't specify.
                # Let's inspect the keys if needed, but standard Ntuple is likely "BremSim;1" or "BremSimData"
                # Wait, analyze_campaign.py usually knows. 
                # Let's try to find keys.
                keys = file.keys()
                tree_name = keys[0] # Take first object
                tree = file[tree_name]
                
                # Arrays: "Energy" and "ParticleID" (0=gamma, 1=e-, 2=e+)
                # We need to bin them.
                
                # Read data
                # Using arrays(library="np")
                data = tree.arrays(["Energy", "ParticleID"], library="np")
                energies_all = data["Energy"]
                pids = data["ParticleID"]
                
                # Photons (PID=0)
                photons = energies_all[pids == 0]
                hist_p, _ = np.histogram(photons, bins=bin_edges)
                
                # Electrons (PID=1)
                electrons = energies_all[pids == 1]
                hist_e, _ = np.histogram(electrons, bins=bin_edges)
                
                records.append({
                    'Energy_MeV': energy,
                    'Thickness_um': thickness,
                    'Photon_Spectrum': hist_p,
                    'Electron_Spectrum': hist_e,
                    'Total_Photons': len(photons),
                    'Total_Electrons': len(electrons)
                })
                
        except Exception as e:
            print(f"Failed to process {root_file}: {e}")
            
    # Create DataFrame
    df = pd.DataFrame(records)
    print(f"Processed {len(df)} simulations.")
    
    # Save
    with open(output_pkl, 'wb') as f:
        pickle.dump(df, f)
    print(f"Saved processed data to {output_pkl}")

if __name__ == "__main__":
    base_dir = "C:\\Geant4_Projects\\BremSim\\post_process"
    data_dir = os.path.join(base_dir, "non_trained")
    bin_edges_path = os.path.join(base_dir, "bin_edges.npy")
    output_pkl = os.path.join(data_dir, "combined_spectra_table.pkl")
    
    process_data(data_dir, bin_edges_path, output_pkl)
