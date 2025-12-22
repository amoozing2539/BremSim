import numpy as np

def generate_macro():
    thicknesses = [
        ("5 um", "5um"),
        ("25 um", "25um"),
        ("50 um", "50um"),
        ("100 um", "100um"),
        ("250 um", "250um"),
        ("500 um", "500um"),
        ("1.0 mm", "1mm"),
        ("1.5 mm", "1.5mm"),
        ("2.0 mm", "2mm"),
        ("3.0 mm", "3mm")
    ]
    
    energies = np.arange(0.1, 5.01, 0.1)
    
    with open("macros/full_run.mac", "w") as f:
        f.write("/run/initialize\n")
        f.write("/run/verbose 0\n")
        f.write("/event/verbose 0\n")
        f.write("/tracking/verbose 0\n\n")
        
        for t_cmd, t_name in thicknesses:
            f.write(f"# Configuration: Thickness {t_cmd}\n")
            f.write(f"/BremSim/det/setFoilThickness {t_cmd}\n")
            f.write("/run/reinitializeGeometry\n\n")
            
            for e in energies:
                e_str = f"{e:.1f}"
                f.write(f"# Energy {e_str} MeV\n")
                f.write(f"/gun/energy {e_str} MeV\n")
                f.write(f"/analysis/setFileName output_E_{e_str}MeV_T_{t_name}.root\n")
                f.write(f"/run/beamOn 1000000\n\n")

if __name__ == "__main__":
    generate_macro()
