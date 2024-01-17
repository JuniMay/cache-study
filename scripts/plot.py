import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
    sns.set(font='Times New Roman', font_scale=1.5,
            style='whitegrid', palette='viridis')

    # plot large graph with each trace as a subplot
    fig, axs = plt.subplots(4, 3, figsize=(20, 15))

    fig.suptitle(metric)

    for i, trace_id in enumerate(result.keys()):
        trace_result = result[trace_id]

        metric_result = {}

        for executable_name in trace_result.keys():
            metric_result[executable_name] = trace_result[executable_name][metric]

        replacements = set()

        for executable_name in metric_result.keys():
            replacements.add(executable_name.split(' ')[0])

        replacements = list(replacements)
        replacements.sort()

        prefetchers = set()

        for executable_name in metric_result.keys():
            prefetchers.add(executable_name.split(' ')[1])

        prefetchers = list(prefetchers)
        prefetchers.sort()

        grouped_result = {}

        for j, prefetcher in enumerate(prefetchers):
            grouped_result[prefetcher] = []

            for replacement in replacements:
                executable_name = f"{replacement} {prefetcher}"

                if executable_name in metric_result:
                    grouped_result[prefetcher].append(
                        metric_result[executable_name])

                else:
                    grouped_result[prefetcher].append(0)

        # plot
        num_prefetchers = len(prefetchers)

        x = np.arange(len(replacements))
        width = 0.15

        axs[i // 3, i % 3].set_title(trace_id)
        axs[i // 3, i % 3].set_xticks(x)
        axs[i // 3, i % 3].set_xticklabels(replacements)
        # axs[i // 3, i % 3].set_ylabel(metric)

        for j, prefetcher in enumerate(prefetchers):
            offset = (j - num_prefetchers // 2) * width
            axs[i // 3, i %
                3].bar(x + offset, grouped_result[prefetcher], width, label=prefetcher)

    # only one legend for the whole figure at bottom right
    handles, labels = axs[2, 1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.88, 0.07))

    # remove empty subplots
    for i in range(4):
        for j in range(3):
            if axs[i, j].get_title() == "":
                fig.delaxes(axs[i, j])

    plt.tight_layout()

    plt.savefig(f"../plots/{metric}.png")
