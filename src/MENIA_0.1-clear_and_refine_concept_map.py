import networkx as nx

from util.config import JAVADOC_GLOBAL_NAME, LATEST_CONCEPT_MAP_PATH, SEALED_CONCEPT_MAP_20210312_PATH
from util.constant import *
from tqdm import tqdm
'''
因为第一次构建的concept map出现了一些失误，有部分的结点没有Ntype属性
这里做一下refine，生成一版新的concept map
'''


def refine_concept_map(doc_name: str):
    '''
    运行之前要先修改LATEST CONCEPT MAP的存储路径
    '''
    old_concept_map = nx.read_gexf(SEALED_CONCEPT_MAP_20210312_PATH[doc_name])
    new_concept_map = nx.MultiDiGraph()
    for node in old_concept_map.nodes:
        if NodeAttributes.Ntype not in old_concept_map.nodes[node].keys():
            continue  # 清洗没有Ntype的结点
        new_concept_map.add_node(node)
        for key, attr in old_concept_map.nodes[node].items():
            new_concept_map.nodes[node][key] = attr  # 复制所有有效结点
    for edge in old_concept_map.edges():
        if EdgeAttrbutes.Etype not in old_concept_map[edge[0]][edge[1]].keys():
            continue  # 清洗无效的边
        edge_index = new_concept_map.add_edge(edge[0], edge[1])
        new_concept_map[edge[0]][edge[1]][edge_index][EdgeAttrbutes.Etype] = old_concept_map[edge[0]
                                                                                             ][edge[1]][EdgeAttrbutes.Etype]
    nx.write_gexf(new_concept_map, LATEST_CONCEPT_MAP_PATH[doc_name])
    print("clear end")
    print("old node amount: ", len(old_concept_map.nodes))
    print("new node amount: ", len(new_concept_map.nodes))
    print("old edge amount: ", len(old_concept_map.edges()))
    print("new edge amount: ", len(new_concept_map.edges()))


if __name__ == "__main__":
    refine_concept_map(JAVADOC_GLOBAL_NAME)
