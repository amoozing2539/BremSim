import torch
import torch.nn as nn
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import re
import uproot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define Model Class (Must match training script)
class BremSpecNet(nn.Module):
    def __init__(self):
        super(BremSpecNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, x):
        return self.net(x)

def load_resources(base_dir):
    # Load Metadata
    meta_path = os.path.join(base_dir, 'model_metadata.pkl')
    if not os.path.exists(meta_path):
        # Fallback to current dir if not found (e.g. running from post_process)
        meta_path = 'model_metadata.pkl'
        
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
        
    # Load Model
    model = BremSpecNet()
    model_path = os.path.join(base_dir, 'brem_spec_net.pth')
    if not os.path.exists(model_path):
        model_path = 'brem_spec_net.pth'
        
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    return model, meta

def predict_spectrum(model, meta, energy_mev, thickness_um, particle_type):
    """
    Generates a full spectrum prediction for a single configuration.
    particle_type: 0 (Photon) or 1 (Electron)
    """
    scaler_X = meta['scaler_X']
    scaler_y = meta['scaler_y']
    bin_centers = meta['bin_centers']
    
    n_bins = len(bin_centers)
    
    # Prepare Input Vectors
    # [Energy, Thickness, Bin_E, Type]
    
    # Create arrays
    energies = np.full(n_bins, energy_mev)
    thicknesses = np.full(n_bins, thickness_um)
    types = np.full(n_bins, particle_type)
    
    # Base Features
    # 0: Energy
    # 1: Thickness (will be logged)
    # 2: Bin Center
    # 3: Type
    
    # Feature 4: Energy - Bin Center (Endpoint Distance)
    # Matches Scaler Mean ~0.02, Var ~4.2
    feat_4 = energies - bin_centers
    
    # Feature 5: (Energy - Bin Center) * Energy
    # Matches Scaler Mean ~2.27, Var ~22.5
    # This represents the endpoint distance weighted by the beam energy.
    feat_5 = feat_4 * energies
    
    # Stack: [E, LogT, Bin, Type, (E-Bin), (E-Bin)*E]
    
    log_thick = np.log10(thicknesses + 1e-6)
    
    X_working = np.column_stack((
        energies, 
        log_thick, 
        bin_centers, 
        types, 
        feat_4, 
        feat_5
    ))
    
    # Scale Inputs
    X_scaled = scaler_X.transform(X_working)
    
    # Convert to Tensor
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    
    # Predict
    with torch.no_grad():
        y_pred_scaled = model(X_tensor).numpy()
    
    # Inverse Scale Targets
    # 1. Inverse MinMax
    y_pred_log = scaler_y.inverse_transform(y_pred_scaled)
    
    # 2. Inverse Log (Expm1)
    y_pred = np.expm1(y_pred_log).flatten()
    
    # Clip negatives (physically impossible)
    y_pred = np.maximum(y_pred, 0)
    
    return bin_centers, y_pred

def parse_filename(filename):
    basename = os.path.basename(filename)
    match = re.search(r"output_E_([\d\.]+)MeV_T_(.+)\.root", basename)
    if match:
        energy = float(match.group(1))
        thickness_str = match.group(2)
        
        # Parse thickness string to float um
        val = float(re.findall(r"[\d\.]+", thickness_str)[0])
        if "mm" in thickness_str:
            val *= 1000.0
        return energy, val
    return None, None

def get_ground_truth_from_root(file_path, bin_edges):
    """
    Loads particle data from ROOT file and bins it according to bin_edges.
    Returns (hist_photons, hist_electrons)
    """
    try:
        with uproot.open(file_path) as file:
            if "Absolute Energies" not in file:
                return None, None
            
            tree = file["Absolute Energies"]
            # Load as numpy arrays directly
            data = tree.arrays(["AbsEnergy", "ParticleID"], library="np")
            
            energies = data["AbsEnergy"]
            pids = data["ParticleID"]
            
            # Filter
            photons = energies[pids == 0]
            electrons = energies[pids == 1]
            
            # Histogram
            # Note: The model predicts counts/density? 
            # Looking at previous code, it seems to predict counts (or log counts).
            # We should check if density=True or False.
            # In predict_spectrum, 'y_pred' is counts (expm1 of log count).
            # So we use density=False.
            
            hist_p, _ = np.histogram(photons, bins=bin_edges)
            hist_e, _ = np.histogram(electrons, bins=bin_edges)
            
            return hist_p, hist_e
            
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return None, None

def evaluate_non_trained(base_dir):
    # Locate Resources
    model_dir = base_dir # Assuming model is in post_process
    
    model, meta = load_resources(model_dir)
    
    # Reconstruct Bin Edges from Centers (assuming uniform)
    bin_centers = meta['bin_centers']
    bin_width = bin_centers[1] - bin_centers[0]
    bin_edges = np.concatenate([
        bin_centers - bin_width/2, 
        [bin_centers[-1] + bin_width/2]
    ])
    
    # Find Non-Trained Files
    non_trained_dir = os.path.join(base_dir, "non_trained")
    pattern = os.path.join(non_trained_dir, "output_E_*_T_*.root")
    files = glob.glob(pattern)
    
    if not files:
        print(f"No files found in {non_trained_dir}")
        return

    print(f"Found {len(files)} files to evaluate.")
    
    output_dir = os.path.join(non_trained_dir, "eval_plots")
    os.makedirs(output_dir, exist_ok=True)
    
    for i, file_path in enumerate(files):
        energy, thickness = parse_filename(file_path)
        if energy is None:
            continue
            
        print(f"[{i+1}/{len(files)}] Evaluating E={energy} MeV, T={thickness} um...")
        
        # Get Ground Truth
        gt_photons, gt_electrons = get_ground_truth_from_root(file_path, bin_edges)
        if gt_photons is None:
            continue
            
        # Get Predictions
        _, pred_photons = predict_spectrum(model, meta, energy, thickness, 0)
        _, pred_electrons = predict_spectrum(model, meta, energy, thickness, 1)
        
        # Plot
        plt.figure(figsize=(10, 6))
        
        # Photons
        plt.step(bin_centers, gt_photons, where='mid', label='Simulated $\gamma$', color='blue', alpha=0.5)
        plt.plot(bin_centers, pred_photons, label='Neural Net $\gamma$', color='blue', linestyle='--', linewidth=2)
        
        # Electrons
        plt.step(bin_centers, gt_electrons, where='mid', label='Simulated $e^-$', color='red', alpha=0.5)
        plt.plot(bin_centers, pred_electrons, label='Neural Net $e^-$', color='red', linestyle='--', linewidth=2)
        
        plt.yscale('log')
        plt.title(f"Model Evaluation: {energy} MeV Beam, {thickness} $\mu$m Foil (Non-Trained)")
        plt.xlabel("Energy (MeV)")
        plt.ylabel("Counts")
        plt.legend()
        plt.grid(True, alpha=0.3, which="both")
        
        # Save
        filename = f"model_evaluation_{energy}MeV_{thickness}um_NonTrained.png"
        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path)
        plt.close()
        
    print(f"All plots saved to {output_dir}")

if __name__ == "__main__":
    # Assume script is in post_process
    script_dir = os.path.dirname(os.path.abspath(__file__))
    evaluate_non_trained(script_dir)
