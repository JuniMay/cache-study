import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

result_dir = '../results'

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


# print(result)

os.makedirs("../plots", exist_ok=True)

# sort result by executable name
for trace_id in result.keys():
    trace_result = result[trace_id]
    result[trace_id] = dict(
        sorted(trace_result.items(), key=lambda item: item[0]))

for metric in ["LLC Hit Rate", "MPKI", "IPC", "Prefetch Accuracy"]:
    # academic style grey and lines
    sns.set_style("whitegrid")
    sns.set_palette("Greys_r")

    # plot large graph with each trace as a subplot
    fig, axs = plt.subplots(3, 3, figsize=(15, 10))
    fig.suptitle(metric)

    for i, trace_id in enumerate(result.keys()):
        trace_result = result[trace_id]

        # plot small graph with each executable as a subplot
        for j, executable_name in enumerate(trace_result.keys()):
            executable_result = trace_result[executable_name]

            axs[i // 3, i % 3].barh(executable_name,
                                    executable_result[metric], height=0.8)
            axs[i // 3, i % 3].set_title(trace_id)

    plt.tight_layout()

    plt.savefig(f"../plots/{metric}.png")
