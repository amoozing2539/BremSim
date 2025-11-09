import uproot
import pandas as pd

# Open the ROOT file
file_path = "C:\\Geant4_Projects\\BremSim\\post_process\\output.root"
root_file = uproot.open(file_path)

# Get the first tree/directory in the file (you might need to adjust the tree name)
tree = root_file[root_file.keys()[0]]

# Convert to pandas DataFrame
df = tree.arrays(library="pd")

# Print the DataFrame to verify
print("DataFrame shape:", df.shape)
print("\nFirst few rows:")
print(df.head())