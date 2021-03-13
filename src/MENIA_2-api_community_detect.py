import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx


from util.config import LATEST_COMMUNITY_MAP_PATH, LATEST_CONCEPT_MAP_PATH, JAVADOC_GLOBAL_NAME


def louvain_community_map(doc_name):
    community_map = nx.read_gexf(LATEST_COMMUNITY_MAP_PATH[doc_name])

    # 用默认参数尝试社群检测
    partition = community_louvain.best_partition(community_map)
    print("default setting, detect community numbers: ", len(partition.keys()))

    # draw the graph
    pos = nx.spring_layout(community_map)
    # color the nodes according to their partition
    cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
    nx.draw_networkx_nodes(community_map, pos, partition.keys(), node_size=2,
                           cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(community_map, pos, alpha=0.4)
    plt.savefig('/media/dell/disk/yinh/SOworkspace/data/cache/community_map.png')


if __name__ == "__main__":
    louvain_community_map(JAVADOC_GLOBAL_NAME)
