import subprocess
import os

root_dir = "../config/combination"
champsim_dir = "../ChampSim"

for subdir, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.json'):
            json_file_path = os.path.join(subdir, file)
            
            command = f"./config.sh {json_file_path}"
            
            subprocess.run(command, shell=True, cwd=champsim_dir)
            subprocess.run("make", shell=True, cwd=champsim_dir)

print("All configurations have been processed.")
