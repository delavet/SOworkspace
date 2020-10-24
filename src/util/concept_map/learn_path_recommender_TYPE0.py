import os
import networkx as nx

from copy import deepcopy
from ..constant import *
from ..config import LATEST_CONCEPT_MAP_PATH, TEMP_FILE_STORE_PATH


def get_related_concepts_submap(concept_map : nx.DiGraph, concept_node : str):
    submap = concept_map.subgraph(list(nx.dfs_postorder_nodes(concept_map, concept_node)))
    #nx.write_gexf(submap, os.path.join(TEMP_FILE_STORE_PATH, str(concept_node) + '_cache.gexf'))
    return submap


def filter_important_concepts_PACKAGE(sub_concept_map: nx.DiGraph):
    candidate_nodes = [node for node in sub_concept_map.nodes if 'Ntype' in sub_concept_map.nodes[node].keys() and sub_concept_map.nodes[node]['Ntype'] in class_level_node_types and sub_concept_map.in_degree(node) < 3]
    out_degrees = {}
    for node in candidate_nodes:
        out_degrees[node] = 0
        succs = sub_concept_map.succ[node]
        for succ in succs:
            if 'Ntype' in sub_concept_map.nodes[succ].keys() and sub_concept_map.nodes[succ]['Ntype'] in class_level_node_types:
                out_degrees[node] = out_degrees[node] + 1
            else:
                out_degrees[node] = out_degrees[node] + sub_concept_map.out_degree(succ)
    l = [(key, value) for key, value in out_degrees.items()]
    l = sorted(l, key=lambda x:x[1], reverse = True)
    result_nodes = []
    for i in range(len(l)):
        if i < 5:
            result_nodes.append(l[i][0])
        else:
            break
    final_ret = set()
    for result_node in result_nodes:
        final_ret.add(result_node)
        edges = sub_concept_map.out_edges(result_node)
        for edge in edges:
            if sub_concept_map[edge[0]][edge[1]]['Etype'] == EdgeType.REFERENCE_IN_DESCRIPTION or sub_concept_map[edge[0]][edge[1]]['Etype'] ==EdgeType.ALSO_SEE:
                final_ret.add(edge[1])
    result_nodes = deepcopy(list(final_ret))
    for result_node in result_nodes:
        dfs_nodes = nx.dfs_postorder_nodes(sub_concept_map, result_node, depth_limit= 2)
        for temp_node in dfs_nodes:
            final_ret.add(temp_node)
    return list(final_ret)


def recommend_learn_concepts_PACKAGE(concept_map: nx.DiGraph, target: str):
    submap = get_related_concepts_submap(concept_map, target)
    important_concepts = filter_important_concepts_PACKAGE(submap)
    recommend_map = submap.subgraph(important_concepts)
    nx.write_gexf(recommend_map, os.path.join(TEMP_FILE_STORE_PATH, str(target) + '_recommend.gexf'))
