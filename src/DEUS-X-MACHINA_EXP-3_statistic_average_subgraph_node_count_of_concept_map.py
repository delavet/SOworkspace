import networkx as nx
import numpy as np

from util.constant import NodeAttributes, class_level_node_types
from tqdm import tqdm
from util.concept_map.common import get_latest_concept_map


def statistic_node_count_of_subgraph_by_step(concept_map: nx.Graph, step: int):
    counts = []
    for node in tqdm(list(concept_map.nodes)):
        if concept_map.nodes[node].get(NodeAttributes.Ntype) not in class_level_node_types:
            continue
        bfs_tree = nx.bfs_tree(concept_map, node, depth_limit=step)
        node_count = len(set([n for n in bfs_tree.nodes if concept_map.nodes[n].get(
            NodeAttributes.Ntype) in class_level_node_types]))
        counts.append(node_count)
    avg_count = np.mean(counts)
    print(f'for step {step}, subgraph size is {avg_count} in average')


if __name__ == "__main__":
    concept_map = nx.Graph(get_latest_concept_map())
    statistic_node_count_of_subgraph_by_step(concept_map, 1)
    statistic_node_count_of_subgraph_by_step(concept_map, 2)
