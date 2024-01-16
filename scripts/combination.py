
import json
import os

from copy import deepcopy

l2c_prefetchers = ["no", "next_line", "ip_stride", "spp_dev", "va_ampm_lite"]
llc_replacements = ["lru", "drrip", "ship", "srrip"]

root_dir = "../config/combination"

os.makedirs(root_dir, exist_ok=True)

base_configuration = {
    "executable_name": "champsim",
    
    "ooo_cpu": [
        {
            "rob_size": 256,
            "fetch_width": 6,
            "decode_width": 3,
            "dispatch_width": 3,
            "execute_width": 3,
            "lq_width": 3,
            "sq_width": 3,
            "retire_width": 3
        }
    ],

    "L1I": {
        "sets": 64,
        "ways": 8,
        "latency": 4,
        "prefetcher": "next_line_instr",
        "replacement": "lru"
    },

    "L1D": {
        "sets": 64,
        "ways": 8,
        "latency": 4,
        "prefetcher": "next_line",
        "replacement": "lru"
    },
    
    
    "L2C": {
        "sets": 512,
        "ways": 8,
        "latency": 12,
        "prefetcher": "no",
        "replacement": "lru"
    },

    "LLC": {
        "sets": 2048,
        "ways": 16,
        "latency": 26,
        "prefetcher": "no",
        "replacement": "lru"
    }
}

for llc_replacement in llc_replacements:
    llc_dir = os.path.join(root_dir, llc_replacement)
    os.makedirs(llc_dir, exist_ok=True)

    for l2c_prefetcher in l2c_prefetchers:
        configuration = deepcopy(base_configuration)
        
        configuration["executable_name"] = f"champsim_{llc_replacement}_{l2c_prefetcher}"
        configuration["L2C"]["prefetcher"] = l2c_prefetcher
        configuration["LLC"]["replacement"] = llc_replacement

        file_name = f"{l2c_prefetcher}.json"
        file_path = os.path.join(llc_dir, file_name)

        with open(file_path, 'w') as json_file:
            json.dump(configuration, json_file, indent=4)

print(f"Configurations have been saved in '{root_dir}' directory.")
