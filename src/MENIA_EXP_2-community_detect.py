import json
import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


from util.config import EXP_COMMUNITY_FREQUENCY_THRESHOLDS, LATEST_COMMUNITY_MAP_PATH, LATEST_CONCEPT_MAP_PATH, JAVADOC_GLOBAL_NAME, COMMUNITY_RECORD_STORE_PATH, base_dir

community_count_map = {}


def log_statitic(freq, res, counts, log):
    log.write("社群统计概况：\n")
    a_mean = np.mean(counts)
    a_var = np.var(counts)
    a_std = np.std(counts)
    a_max = np.max(counts)
    a_min = np.min(counts)
    a_mid = np.median(counts)
    log.write(f"[{freq},{res}] 社群数量：{len(counts)}\n")
    log.write(f"[{freq},{res}] 平均API数量：{a_mean}\n")
    log.write(f"[{freq},{res}] 社群API数量方差：{a_var}\n")
    log.write(f"[{freq},{res}] 社群API数量标准差：{a_std}\n")
    log.write(f"[{freq},{res}] 社群API数量波动范围：{a_min} - {a_max}\n")
    log.write(f"[{freq},{res}] 社群API数量中位数：{a_mid}\n")


def louvain_community_map(doc_name, COMMUNITY_THRESHOLD, RESOLUTION, log):
    global community_count_map
    print(f"community_threshold: {COMMUNITY_THRESHOLD}, resolution: {RESOLUTION}")
    log.write(
        f"===community_threshold: {COMMUNITY_THRESHOLD}, resolution: {RESOLUTION}===\n")

    community_map = nx.read_gexf(
        f"{base_dir}/data/exp/community_map_thresold_{COMMUNITY_THRESHOLD}.gexf")

    # 用默认参数尝试社群检测
    partition = community_louvain.best_partition(community_map, resolution=RESOLUTION)
    print(f"resolution {RESOLUTION}, detect community numbers: ",
          len(set(partition.values())))
    community_count_map[RESOLUTION][COMMUNITY_THRESHOLD] = len(
        set(partition.values()))
    community_count = {}
    community_record = {}
    for k, v in partition.items():
        community_map.nodes[k]['subset'] = v
        community_count[v] = community_count.get(v, 0) + 1
        if v not in community_record.keys():
            community_record[v] = []
        community_record[v].append(k)
    counts = list(community_count.values())
    log_statitic(COMMUNITY_THRESHOLD, RESOLUTION, counts, log)
    with open(f'{base_dir}/data/exp/cache/community_count_thres_{COMMUNITY_THRESHOLD}_res_{RESOLUTION}.json', 'w', encoding='utf-8') as wf_c, open(f'{base_dir}/data/exp/community_record_thres_{COMMUNITY_THRESHOLD}_res_{RESOLUTION}.json', 'w', encoding='utf-8') as wf_r:
        json.dump(community_count, wf_c, indent=2, ensure_ascii=False)
        json.dump(community_record, wf_r, indent=2, ensure_ascii=False)

    # draw the graph
    pos = nx.multipartite_layout(community_map)
    # color the nodes according to their partition
    cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
    nx.draw_networkx_nodes(community_map, pos, partition.keys(), node_size=2,
                           cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(community_map, pos, alpha=0.4)
    plt.savefig(
        f'{base_dir}/data/exp/cache/community_figure_thres_{COMMUNITY_THRESHOLD}_res_{RESOLUTION}.png')


if __name__ == "__main__":
    log = open(f"{base_dir}/data/exp/MENIA_louvain_log.log", 'w', encoding='utf-8')
    freqs = EXP_COMMUNITY_FREQUENCY_THRESHOLDS
    resolutions = [0.1, 0.3, 0.5, 0.8, 1, 1.5, 2, 5, 10]
    for res in resolutions:
        community_count_map[res] = {}
        for freq in freqs:
            community_count_map[res][freq] = 0
    for freq in freqs:
        for res in resolutions:
            louvain_community_map(JAVADOC_GLOBAL_NAME, freq, res, log)
    table = pd.DataFrame(community_count_map)
    writer = pd.ExcelWriter(f'{base_dir}/data/exp/MENIA_community_count_record.xlsx')
    table.to_excel(writer)
    writer.save()
    log.close()
