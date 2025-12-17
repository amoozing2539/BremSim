#%%
from typing import List, Optional
import pandas as pd
import uproot
import numpy as np
import matplotlib.pyplot as plt

file_path = "../build/output_E_0.1MeV_T_5um.root"

#%%
# Open ROOT file and load the trees
with uproot.open(file_path) as root_file:
    # Load Events ntuple (primary particle information)
    events_tree = root_file["Absolute Energies"]
    events_df = events_tree.arrays(library="pd")

    # Load Hits ntuple (detector hit information)
    hits_tree = root_file["Relative Energies"]
    hits_df = hits_tree.arrays(library="pd")

#%%
# Filter particle types
# Secondary gammas: PDG==22 and ParentID>0
primary_electrons = events_df[(events_df['PDGCode'] == 11) & (events_df['ParentID'] == 0)]
secondary_gammas = events_df[(events_df['PDGCode'] == 22) & (events_df['ParentID'] > 0)]
secondary_electrons = events_df[(events_df['PDGCode'] == 11) & (events_df['ParentID'] > 0)]
secondary_positrons = events_df[(events_df['PDGCode'] == -11) & (events_df['ParentID'] > 0)]

print(f"Total steps in filtered data:")
print(f"  Primary electrons: {len(primary_electrons)}")
print(f"  Secondary gammas (ParentID>0): {len(secondary_gammas)}")
print(f"  Secondary electrons: {len(secondary_electrons)}")
print(f"  Secondary positrons: {len(secondary_positrons)}")

#%% Get the last step for each particle (identified by EventID + TrackID)
def get_escape_energy(df: pd.DataFrame) -> np.ndarray:
    """
    Get the final FinEnergy for each unique particle.
    Each particle is uniquely identified by (EventID, TrackID).
    This represents the energy the particle escaped with.
    """
    if df.empty:
        return np.array([])
    
    # Group by EventID and TrackID to get the last step for each unique particle
    last_steps = df.groupby(['EventID', 'TrackID']).last().reset_index()
    
    # Get FinEnergy values where FinEnergy > 0 (particle escaped)
    escape_energies = last_steps[last_steps['FinEnergy'] > 0]['FinEnergy'].values
    
    return escape_energies

prime_electron_energies = get_escape_energy(primary_electrons)
gamma_energies = get_escape_energy(secondary_gammas)
electron_energies = get_escape_energy(secondary_electrons)
positron_energies = get_escape_energy(secondary_positrons)

print(f"\nParticles that escaped (FinEnergy > 0):")
print(f"  Primary electrons: {len(prime_electron_energies)}")
print(f"  Secondary gammas: {len(gamma_energies)}")
print(f"  Secondary electrons: {len(electron_energies)}")
print(f"  Secondary positrons: {len(positron_energies)}")

#%% Determine global binning range
all_energies = np.concatenate([prime_electron_energies, gamma_energies, electron_energies, positron_energies])

if len(all_energies) == 0:
    print("\nNo escape data found!")
else:
    min_energy = 0
    max_energy = np.max(all_energies) * 1.05  # 5% margin
    n_bins = 50
    bin_edges = np.linspace(min_energy, max_energy, n_bins + 1)
    bin_width = bin_edges[1] - bin_edges[0]  # Calculate bin width

    #%% Histogram each particle type using the same bins
    prime_e_counts, _ = np.histogram(prime_electron_energies, bins=bin_edges)
    gamma_counts, _ = np.histogram(gamma_energies, bins=bin_edges)
    sec_e_counts, _ = np.histogram(electron_energies, bins=bin_edges)
    sec_p_counts, _ = np.histogram(positron_energies, bins=bin_edges)
    
    # Normalize by bin width to get density
    prime_e_density = prime_e_counts / bin_width
    gamma_density = gamma_counts / bin_width
    sec_e_density = sec_e_counts / bin_width
    sec_p_density = sec_p_counts / bin_width
    
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    #%% Plot curves
    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers, prime_e_density + 1e-10, drawstyle='steps-mid', label='Primary e⁻', linewidth=2)
    plt.plot(bin_centers, gamma_density + 1e-10, drawstyle='steps-mid', label='Secondary γ', linewidth=2)
    plt.plot(bin_centers, sec_e_density + 1e-10, drawstyle='steps-mid', label='Secondary e⁻', linewidth=2)
    #plt.plot(bin_centers, sec_p_density + 1e-10, drawstyle='steps-mid', label='Secondary e⁺', linewidth=2)
    
    plt.xlabel("Final Kinetic Energy [MeV]", fontsize=12)
    plt.ylabel("Counts per MeV", fontsize=12)
    plt.title("Escape Energy Distribution of Secondary Particles for 5MeV e- Beam", fontsize=14)
    plt.yscale('log')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend(fontsize=10)
    plt.ylim(1e1,1e7)
    plt.tight_layout()
    plt.show()
# %%
