import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

WARMUP_INSTRUCTIONS = 200000000
SIMULATION_INSTRUCTIONS = 500000000

def run_single(bin_path: str, trace: str, output: str, stdout: str = None):
    command = f'{bin_path} --warmup-instructions {WARMUP_INSTRUCTIONS} --simulation-instructions {SIMULATION_INSTRUCTIONS} --json {output} {trace}'
    print(command)
    # redirect stdout to a text file
    with open(stdout, 'w') as stdout:
        res = subprocess.Popen(command, shell=True,
                               stdout=stdout, stderr=stdout).wait()

    if res != 0:
        print(f"Error when running {bin_path} with {trace} trace.")
    else:
        print(f"Successfully run {bin_path} with {trace} trace.")


trace_dir = "../traces"
bin_dir = "../ChampSim/bin"
# bin_names = ["champsim_unified_llc", "champsim_rlr_va_ampm_lite"]
bin_names = ["champsim_unified_next_line"]

os.makedirs("../results_unified", exist_ok=True)

with ThreadPoolExecutor(max_workers=10) as executor:
    for subdir, dirs, files in os.walk(trace_dir):
        for file in files:
            if file.endswith('.champsimtrace.xz'):
                if file.startswith('433'):
                    continue
                # make dir first
                trace_id = file.split('.')[0]
                trace_dir = os.path.join("../results_unified", trace_id)
                os.makedirs(trace_dir, exist_ok=True)

                # run
                for bin_file in bin_names:
                    bin_path = os.path.join(bin_dir, bin_file)
                    trace_path = os.path.join(subdir, file)
                    stdout_path = os.path.join(trace_dir, f"{bin_file}.txt")
                    output_path = os.path.join(trace_dir, f"{bin_file}.json")

                    executor.submit(run_single, bin_path,
                                    trace_path, output_path, stdout_path)

print("All configurations have been processed.")
