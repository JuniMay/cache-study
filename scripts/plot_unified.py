import json
import os

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


result_dir = '../results_unified'

result = {}

for subdir, dirs, files in os.walk(result_dir):
    for trace_id in dirs:
        # iterate all json under this trace_id
        trace_dir = os.path.join(result_dir, trace_id)
        result[trace_id] = {}
        for file in os.listdir(trace_dir):
            if file.endswith('.json'):
                json_file_path = os.path.join(trace_dir, file)
                with open(json_file_path) as json_file:
                    data = json.load(json_file)

                    executable_name = file.split('.')[0].split(
                        '_', 1)[1].replace('_', ' ', 1).replace('_', '-')
                    result[trace_id][executable_name] = {}

                    llc = data[0]['sim']['LLC']
                    l2c = data[0]['sim']['cpu0_L2C']

                    llc_total_hit = 0
                    llc_total_miss = 0

                    for key in ["LOAD", "RFO", "TRANSLATION", "WRITE"]:
                        llc_total_hit += llc[key]['hit'][0]
                        llc_total_miss += llc[key]['miss'][0]

                    cycles = data[0]['sim']['cores'][0]['cycles']
                    instructions = data[0]['sim']['cores'][0]['instructions']

                    result[trace_id][executable_name]['LLC Hit Rate'] = (llc_total_hit /
                                                                         (llc_total_hit + llc_total_miss))
                    result[trace_id][executable_name]['MPKI'] = (
                        llc_total_miss / instructions) * 1000
                    result[trace_id][executable_name]['IPC'] = instructions / cycles
                    try:
                        result[trace_id][executable_name]['Prefetch Accuracy'] = l2c['useful prefetch'] / (
                            l2c['useful prefetch'] + l2c['useless prefetch'])
                    except ZeroDivisionError:
                        result[trace_id][executable_name]['Prefetch Accuracy'] = 0
                        

# calculate IPC speedup compare to lru no prefetch
for trace_id in result.keys():
    trace_result = result[trace_id]
    
    if 'rlr va-ampm-lite' not in trace_result:
        continue

    lru_no_prefetch_ipc = trace_result['rlr va-ampm-lite']['IPC']

    for executable_name in trace_result.keys():
        trace_result[executable_name]['IPC Speedup'] = (
            trace_result[executable_name]['IPC'] - lru_no_prefetch_ipc) / lru_no_prefetch_ipc

os.makedirs('../plots_unified', exist_ok=True)

# different metrics in different subplots,
# each subplot contain all traces

sns.set(font='Times New Roman', font_scale=1.5,
        style='whitegrid', palette='Greys_r')
fig, axs = plt.subplots(1, 3, figsize=(18, 5))

for i, metric in enumerate(['MPKI', "IPC Speedup", "LLC Hit Rate"]):
    num_trace = len(result.keys())
    
    x = np.arange(num_trace)
    width = 0.2
    
    y_vanilla = []
    y_unified = []
    y_unified_next_line = []
    
    for trace_id in result.keys():
        trace_result = result[trace_id]
                
        if 'rlr va-ampm-lite' in trace_result and metric in trace_result['rlr va-ampm-lite']:
            y_vanilla.append(trace_result['rlr va-ampm-lite'][metric])
        else:
            y_vanilla.append(0)
            
        if 'unified llc' in trace_result and metric in trace_result['unified llc']:
            y_unified.append(trace_result['unified llc'][metric])
        else:
            y_unified.append(0)
            
        if 'unified next-line' in trace_result and metric in trace_result['unified next-line']:
            y_unified_next_line.append(trace_result['unified next-line'][metric])
        else:
            y_unified_next_line.append(0)
                
    assert len(y_vanilla) == len(y_unified)
    assert len(y_vanilla) == num_trace
                

    axs[i].bar(x - width, y_vanilla, width, label='rlr va-ampm-lite')
    axs[i].bar(x, y_unified, width, label='unified va-ampm-lite')
    axs[i].bar(x + width, y_unified_next_line, width, label='unified next-line')
    
    
    axs[i].set_xticks(x)
    axs[i].set_xticklabels(result.keys())
    axs[i].set_xlabel('Trace')
    axs[i].set_ylabel(metric)

axs[1].legend(loc='lower right')

    
plt.tight_layout()
plt.savefig('../plots_unified/metrics.png')