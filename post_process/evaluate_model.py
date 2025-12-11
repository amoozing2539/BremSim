import torch
import torch.nn as nn
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define Model Class (Must match training script)
class BremSpecNet(nn.Module):
    def __init__(self):
        super(BremSpecNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
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
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
        
    # Load Model
    model = BremSpecNet()
    model_path = os.path.join(base_dir, 'brem_spec_net.pth')
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
    
    # Stack features
    X_raw = np.column_stack((energies, thicknesses, bin_centers, types))
    
    # Log transform thickness (Same as training)
    X_working = X_raw.copy()
    X_working[:, 1] = np.log10(X_working[:, 1] + 1e-6)
    
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

def evaluate_and_plot(base_dir):
    model, meta = load_resources(base_dir)
    
    # Load original data for Ground Truth comparison
    pkl_path = os.path.join(os.path.dirname(base_dir), "combined_spectra_table.pkl")
    if not os.path.exists(pkl_path):
         pkl_path = "C:\\Geant4_Projects\\BremSim\\combined_spectra_table.pkl"
         
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
        
    # Select a few Test Cases
    test_cases = [
        {'E': 1.0, 'T': 50.0},
        {'E': 2.0, 'T': 2000.0},
        {'E': 4.5, 'T': 250.0}
    ]
    
    plt.figure(figsize=(15, 10))
    
    for i, case in enumerate(test_cases):
        target_E = case['E']
        target_T = case['T']
        
        # Get Ground Truth
        # Find closest match in data
        subset = data[(np.isclose(data['Energy_MeV'], target_E)) & (np.isclose(data['Thickness_um'], target_T))]
        
        if subset.empty:
            print(f"Skipping case {case}, not found in data.")
            continue
            
        row = subset.iloc[0]
        gt_photon = row['Photon_Spectrum']
        gt_electron = row['Electron_Spectrum']
        
        # Generate Predictions
        bins, pred_photon = predict_spectrum(model, meta, target_E, target_T, 0)
        _, pred_electron = predict_spectrum(model, meta, target_E, target_T, 1)
        
        # Plot
        plt.subplot(2, 2, i+1)
        
        # Photons
        plt.step(bins, gt_photon, where='mid', label='Truth $\gamma$', color='blue', alpha=0.5)
        plt.plot(bins, pred_photon, label='Pred $\gamma$', color='blue', linestyle='--')
        
        # Electrons
        plt.step(bins, gt_electron, where='mid', label='Truth $e^-$', color='red', alpha=0.5)
        plt.plot(bins, pred_electron, label='Pred $e^-$', color='red', linestyle='--')
        
        plt.title(f"E={target_E} MeV, T={target_T} $\mu$m")
        plt.yscale('log')
        plt.xlabel("Energy (MeV)")
        plt.ylabel("Counts")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(bottom=1) # Log scale safety
        
    plt.tight_layout()
    plt.savefig('model_evaluation.png')
    print("Saved evaluation plot to model_evaluation.png")

if __name__ == "__main__":
    base_dir = "C:\\Geant4_Projects\\BremSim\\post_process"
    if os.getcwd() == base_dir:
        evaluate_and_plot(".")
    else:
        evaluate_and_plot(base_dir)
