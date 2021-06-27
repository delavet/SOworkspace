import json
import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx


from util.config import LATEST_COMMUNITY_MAP_PATH, LATEST_CONCEPT_MAP_PATH, JAVADOC_GLOBAL_NAME, COMMUNITY_RECORD_STORE_PATH, base_dir


def louvain_community_map(doc_name):
    community_map = nx.read_gexf(LATEST_COMMUNITY_MAP_PATH[doc_name])

    # 用默认参数尝试社群检测
    partition = community_louvain.best_partition(community_map, resolution=0.1)
    print("default setting, detect community numbers: ",
          len(set(partition.values())))
    community_count = {}
    community_record = {}
    for k, v in partition.items():
        community_map.nodes[k]['subset'] = v
        community_count[v] = community_count.get(v, 0) + 1
        if v not in community_record.keys():
            community_record[v] = []
        community_record[v].append(k)
    with open(f'{base_dir}/data/cache/community_count.json', 'w', encoding='utf-8') as wf_c, open(COMMUNITY_RECORD_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_r:
        json.dump(community_count, wf_c, indent=2, ensure_ascii=False)
        json.dump(community_record, wf_r, indent=2, ensure_ascii=False)

    # draw the graph
    pos = nx.multipartite_layout(community_map)
    # color the nodes according to their partition
    cmap = cm.get_cmap('tab20', max(partition.values()) + 1)
    nx.draw_networkx_nodes(community_map, pos, partition.keys(), node_size=2,
                           cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(community_map, pos, alpha=0.4)
    plt.savefig(f'{base_dir}/data/cache/community_map.png')


if __name__ == "__main__":
    louvain_community_map(JAVADOC_GLOBAL_NAME)
