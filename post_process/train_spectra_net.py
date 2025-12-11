import torch
import torch.nn as nn
import torch.optim as optim
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import os

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def load_data(pickle_path, bin_edges_path):
    print(f"Loading data from {pickle_path}...")
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
        
    print(f"Loading bin edges from {bin_edges_path}...")
    bin_edges = np.load(bin_edges_path)
    # Calculate bin centers
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return data, bin_centers

def prepare_pointwise_data(data, bin_centers):
    """
    Explodes the dataset so each bin becomes a sample.
    Inputs: [Beam_Energy, Thickness, Bin_Energy, Particle_Type_ID]
    Output: [Bin_Value]
    Particle_Type_ID: 0 for Photons, 1 for Electrons
    """
    print("re-structuring data into pointwise format (this may take a moment)...")
    
    X_list = []
    y_list = []
    
    # Pre-compute bin center array to tile
    n_bins = len(bin_centers)
    
    # Iterate through simulations
    # Using list comprehension or numpy operations for speed
    
    # 1. Prepare Photons (Type 0)
    # Stack all photon spectra: Shape (N_sims, N_bins)
    photon_spectra = np.vstack(data['Photon_Spectrum'].values)
    n_sims = len(data)
    
    # Create input grids
    # Repeat beam energy and thickness for each bin
    beam_energies = data['Energy_MeV'].values # (N_sims,)
    thicknesses = data['Thickness_um'].values # (N_sims,)
    
    # Tile them to match (N_sims, N_bins)
    beam_grid = np.repeat(beam_energies[:, np.newaxis], n_bins, axis=1)
    thick_grid = np.repeat(thicknesses[:, np.newaxis], n_bins, axis=1)
    bin_grid = np.tile(bin_centers, (n_sims, 1))
    type_grid = np.zeros_like(beam_grid) # 0 for photons
    
    # Flatten everything
    X_photons = np.column_stack((
        beam_grid.flatten(),
        thick_grid.flatten(),
        bin_grid.flatten(),
        type_grid.flatten()
    ))
    y_photons = photon_spectra.flatten()
    
    # 2. Prepare Electrons (Type 1)
    electron_spectra = np.vstack(data['Electron_Spectrum'].values)
    type_grid_e = np.ones_like(beam_grid) # 1 for electrons
    
    X_electrons = np.column_stack((
        beam_grid.flatten(),
        thick_grid.flatten(),
        bin_grid.flatten(),
        type_grid_e.flatten()
    ))
    y_electrons = electron_spectra.flatten()
    
    # Combine
    X = np.vstack((X_photons, X_electrons))
    y = np.concatenate((y_photons, y_electrons))
    
    print(f"Total Data Points Generated: {len(y)}")
    return X, y

class BremSpecNet(nn.Module):
    def __init__(self):
        super(BremSpecNet, self).__init__()
        # Inputs: Beam_E, Thick, Bin_E, Type (4 inputs)
        
        # We use a Residual block style or deeper MLP for better function approximation
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
            nn.Linear(64, 1) # Output: Scalar intensity
        )
        
    def forward(self, x):
        return self.net(x)

def train_model(pickle_path, bin_edges_path):
    data, bin_centers = load_data(pickle_path, bin_edges_path)
    X, y = prepare_pointwise_data(data, bin_centers)
    
    # Filter out zero-value bins to reduce noise? 
    # Optional: For now, we keep them so the model learns where flux is zero.
    # However, log-scaling inputs is often helpful for Energy ranges.
    
    # Normalize Inputs
    # Beam E: 0.1 - 5.0
    # Thickness: 5 - 2000 (Huge range!) -> Log scale might be better for thickness
    # Bin E: 0 - 5.0
    
    # Let's log-transform Thickness for the scaler
    X[:, 1] = np.log10(X[:, 1] + 1e-6) # Log thickness
    
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    
    # Normalize Targets
    # Spectra counts vary by orders of magnitude (0 to 100,000)
    # Log-transforming targets is CRITICAL for spectra
    # We add +1 to handle zeros safely
    y_log = np.log1p(y)
    
    # We can further scale the log-values to approx [0,1] or standardization
    scaler_y = MinMaxScaler()
    y_scaled = scaler_y.fit_transform(y_log.reshape(-1, 1))
    
    print(f"Input Features (post-scaling) mean: {np.mean(X_scaled, axis=0)}")
    print(f"Target (post-scaling) max: {np.max(y_scaled)}")
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.1, random_state=42, shuffle=True
    )
    
    # Convert to Tensors
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32).to(device)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).to(device)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).to(device)
    
    # Initialize Model
    model = BremSpecNet().to(device)
    # print(model)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0005)
    
    # Training Loop
    epochs = 50 # 50 epochs is plenty for 250k points usually
    batch_size = 4096 # Large batch size for speed
    
    train_points = len(X_train)
    num_batches = int(np.ceil(train_points / batch_size))
    
    train_losses = []
    val_losses = []
    
    print(f"Starting training on {train_points} samples...")
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        
        # Shuffle indices
        indices = torch.randperm(train_points)
        
        for i in range(num_batches):
            idx = indices[i*batch_size : (i+1)*batch_size]
            batch_X = X_train_tensor[idx]
            batch_y = y_train_tensor[idx]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_train_loss = epoch_loss / num_batches
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_test_tensor)
            val_loss = criterion(val_outputs, y_test_tensor)
        
        train_losses.append(avg_train_loss)
        val_losses.append(val_loss.item())
        
        print(f'Epoch [{epoch+1}/{epochs}], Train Loss: {avg_train_loss:.6f}, Val Loss: {val_loss.item():.6f}')
            
    # Plotting results
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('MSE Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig('training_loss.png')
    print("Saved training_loss.png")
    
    # Save Model
    torch.save(model.state_dict(), 'brem_spec_net.pth')
    
    # Save Scalers for inference
    with open('model_metadata.pkl', 'wb') as f:
        pickle.dump({
            'scaler_X': scaler_X,
            'scaler_y': scaler_y,
            'bin_centers': bin_centers
        }, f)
    print("Saved model and metadata.")

if __name__ == "__main__":
    base_dir = "C:\\Geant4_Projects\\BremSim\\post_process"
    pkl_path = os.path.join(os.path.dirname(__file__), "..", "combined_spectra_table.pkl")
    bin_edges_path = os.path.join(base_dir, "bin_edges.npy")
    
    # Fallbacks if running from different cwd
    if not os.path.exists(bin_edges_path):
        bin_edges_path = "bin_edges.npy"

    if os.path.exists(pkl_path) and os.path.exists(bin_edges_path):
        train_model(pkl_path, bin_edges_path)
    else:
        print(f"Error: Data files not found.")
        print(f"Pickle: {pkl_path}")
        print(f"Bin Edges: {bin_edges_path}")
