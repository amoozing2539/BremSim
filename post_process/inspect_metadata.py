import pickle
import numpy as np
import os

def inspect_metadata():
    path = os.path.join("post_process", "model_metadata.pkl")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    with open(path, 'rb') as f:
        meta = pickle.load(f)
        
    scaler = meta['scaler_X']
    
    print("Scaler Mean:", scaler.mean_)
    print("Scaler Scale:", scaler.scale_)
    print("Scaler Var:", scaler.var_)
    
    # Also check what's in 'bin_centers' just in case
    print("Bin Centers shape:", meta['bin_centers'].shape)

if __name__ == "__main__":
    inspect_metadata()
