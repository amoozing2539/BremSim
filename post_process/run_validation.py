import os
import subprocess
import time
import re
import csv
import sys

def run_simulation(exe_path, macro_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Running simulation...")
    print(f"Executable: {exe_path}")
    print(f"Macro: {macro_path}")
    print(f"Output Dir: {output_dir}")
    
    # Change CWD to output dir so ROOT files are saved there
    original_cwd = os.getcwd()
    os.chdir(output_dir)
    
    start_time_global = time.time()
    
    # Run Command
    # Note: Geant4 args might be positional.
    cmd = [exe_path, macro_path, "-t", "48"]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Store run times
    run_log = []
    current_run_id = -1
    run_start_time = 0
    
    # File name parser regex (to associate runs with files if possible, 
    # but Geant4 stdout doesn't always show filename clearly unless we parsed the macro beforehand.
    # We will just log Run ID vs Duration for now, and rely on file timestamps or sequential order).
    
    # Regex to catch "Run #0 starts."
    run_start_pattern = re.compile(r"Run #(\d+) starts")
    # Regex to catch "Run #0 ends." (or "Run termination")
    # Actually locally "Run #0 starts." ... [Output] ... "Run #0 starts." (next run)
    
    print("--- Simulation Output ---")
    try:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                # print(line.strip()) # Optional: Print all logs (spammy)
                
                # Check for run start
                m_start = run_start_pattern.search(line)
                if m_start:
                    if current_run_id != -1:
                        # Previous run finished
                        duration = time.time() - run_start_time
                        print(f"Run #{current_run_id} finished. Duration: {duration:.2f}s")
                        run_log.append({'run_id': current_run_id, 'duration_s': duration})
                        
                    current_run_id = int(m_start.group(1))
                    run_start_time = time.time()
                    print(f"--> Run #{current_run_id} started...")
                    
        # Last run
        if current_run_id != -1:
            duration = time.time() - run_start_time
            print(f"Run #{current_run_id} finished. Duration: {duration:.2f}s")
            run_log.append({'run_id': current_run_id, 'duration_s': duration})
            
    except Exception as e:
        print(f"Error during execution: {e}")
        
    end_time_global = time.time()
    print(f"Total Simulation Time: {end_time_global - start_time_global:.2f}s")
    
    os.chdir(original_cwd)
    
    # Save Log
    csv_path = os.path.join(output_dir, "run_times.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['run_id', 'duration_s'])
        writer.writeheader()
        writer.writerows(run_log)
        
    print(f"Run times saved to {csv_path}")

if __name__ == "__main__":
    exe = r"c:\Geant4_Projects\BremSim\build\Release\BremSim.exe"
    macro = r"c:\Geant4_Projects\BremSim\macros\non_trained_run.mac"
    out_dir = r"c:\Geant4_Projects\BremSim\post_process\non_trained"
    
    run_simulation(exe, macro, out_dir)
