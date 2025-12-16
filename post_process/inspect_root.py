import uproot
import os
import glob

def check_root_file():
    data_dir = r"C:\Geant4_Projects\BremSim\post_process\non_trained"
    files = glob.glob(os.path.join(data_dir, "*.root"))
    
    if not files:
        print("No ROOT files found.")
        return
        
    f = files[0]
    print(f"Inspecting: {f}")
    
    with uproot.open(f) as file:
        print("Keys present in file:", file.keys())
        # Try to open the first one
        if file.keys():
            first_key = file.keys()[0]
            obj = file[first_key]
            print(f"Object type: {type(obj)}")
            if hasattr(obj, "keys"):
                print(f"Keys in {first_key}:", obj.keys())
            if hasattr(obj, "show"):
                obj.show()

if __name__ == "__main__":
    check_root_file()
