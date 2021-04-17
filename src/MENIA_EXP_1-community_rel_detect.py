import json
import networkx as nx

from tqdm import tqdm
from util.constant import *
from util.utils import get_api_extreme_short_name_from_entity_id
from util.config import EXP_COMMUNITY_FREQUENCY_THRESHOLDS, LATEST_CONCEPT_MAP_PATH, LATEST_COMMUNITY_MAP_PATH, MENIA_CLASS_LEVEL_PREDICTION_STORE_PATH, MENIA_WHOLE_PREDICTION_STORE_PATH, JAVADOC_GLOBAL_NAME, COMMUNITY_FREQUENCY_STORE_PATH, API_THREAD_ID_MAP_STORE_PATH, base_dir
'''
MENIA：基于社区内API之间关系的API post学习推荐算法

MENIA-1
根据EZA-pipeline的最终预测结果，为concept map添加社区之间的关系
'''

# COMMUNITY_THRESHOLD = 5  # 决定两API共现超过多少次就算紧密关系的
MODE = 'class'
# 是使用转化后的只有类的api链接纪录还是使用原始的api链接纪录
USE_MENIA_PREDICTION_PATH = MENIA_CLASS_LEVEL_PREDICTION_STORE_PATH if MODE == 'class' else MENIA_WHOLE_PREDICTION_STORE_PATH


def copy_node(community_map: nx.Graph, concept_map: nx.MultiDiGraph, node: str):
    '''
    由concept map向community map拷贝结点
    '''
    if node in community_map.nodes:
        return
    community_map.add_node(node)
    for key, attr in concept_map.nodes[node].items():
        community_map.nodes[node][key] = attr


def add_community_rel_heuristic_1(doc_name: str, COMMUNITY_THRESHOLD, log):
    '''
    启发式地向concept map中添加社区关系，使用启发式算法V1
    ## 启发式算法V1
    两个API在社区的同一个thread中同时出现超过COMMUNITY_THRESHOLD次

    生成的community map暂且定为是无向图，因为没感觉到设为有向图的必要

    生成的COOCCUR的关系同时也被加入到concept map中，此时边的方向是社区频率高的指向低的api
    '''
    # global COMMUNITY_THRESHOLD
    log.write(f"===community cooccur threshold {COMMUNITY_THRESHOLD}===\n")
    with open(MENIA_WHOLE_PREDICTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        EZA_predictions = dict(json.load(rf))
    concept_map = nx.MultiDiGraph(
        nx.read_gexf(LATEST_CONCEPT_MAP_PATH[doc_name]))
    community_map = nx.Graph()
    community_frequency = {}
    api_thread_id_map = {} # API和对应的thread的信息，这个信息没有加入图谱（控制图谱数据量），而是单独存成了一个文件，而共现的API对应的thread信息是加入到community map中的
    cooccur_map = {}
    for thread_id, prediction in EZA_predictions.items():
        apis = list(prediction.values())
        for api in apis:
            community_frequency[api] = community_frequency.get(api, 0) + 1
            if api not in api_thread_id_map.keys():
                api_thread_id_map[api] = []
            api_thread_id_map[api].append(thread_id)
    print(f"found all {len(community_frequency.keys())} predicted apis")
    print("dumping community frequency and api-thread map")
    with open(f"{base_dir}/data/exp/community_frequency.json", 'w', encoding='utf-8') as wf:
        json.dump(community_frequency, wf, ensure_ascii=False, indent=2)
    with open(f"{base_dir}/data/exp/api_thread_id_map.json", 'w', encoding='utf-8') as wf:
        json.dump(api_thread_id_map, wf, ensure_ascii=False, indent=2)
    print("community frequency and api-thread map dumped")
    # all_apis = list(community_frequency.keys())
    print("detecting cooccur relationships")
    for thread_id, prediction in tqdm(list(EZA_predictions.items())):
        temp_apis = list(prediction.values())
        for api1 in temp_apis:
            if api1 not in cooccur_map.keys():
                cooccur_map[api1] = {}
            for api2 in temp_apis:
                cooccur_map[api1][api2] = cooccur_map[api1].get(api2, 0) + 1
    print("generating community map nodes")
    for cooccur_api in tqdm(list(cooccur_map.keys())):
        if cooccur_api not in concept_map.nodes:
            continue
        copy_node(community_map, concept_map, cooccur_api)
    print("generating cooccur edge in community map")
    for cooccur_api1 in tqdm(list(cooccur_map.keys())):
        for cooccur_api2 in cooccur_map[cooccur_api1]:
            if cooccur_api2 in community_map.adj[cooccur_api1].keys() or get_api_extreme_short_name_from_entity_id(cooccur_api1) == get_api_extreme_short_name_from_entity_id(cooccur_api2): # 也排除了两个短名相同的API共同出现的情况，最大限度防止ANEMONE预测失误的干扰
                continue
            cooccur_freq = cooccur_map[cooccur_api1][cooccur_api2]
            if cooccur_freq > COMMUNITY_THRESHOLD:
                # 向communtiy map加入信息
                community_map.add_edge(cooccur_api1, cooccur_api2)
                community_map[cooccur_api1][cooccur_api2][EdgeAttrbutes.Etype] = EdgeType.COOCCUR
                community_map[cooccur_api1][cooccur_api2][EdgeAttrbutes.COOCCUR_FREQUENCY] = cooccur_freq
                thread_ids1 = set(api_thread_id_map[cooccur_api1])
                thread_ids2 = set(api_thread_id_map[cooccur_api2])
                cooccur_threads = list(thread_ids1 & thread_ids2) # 把两个API共同出现过的thread id加入到COMMUNITY MAP图谱中去
                community_map[cooccur_api1][cooccur_api2][EdgeAttrbutes.COOCCUR_THREADS] = ','.join(cooccur_threads)
    to_remove_nodes = []
    for node in community_map.nodes:
        if len(community_map.adj[node]) == 0:
            to_remove_nodes.append(node)  # 孤立的API太多了，尝试去掉孤立的API
    community_map.remove_nodes_from(to_remove_nodes)
    print(f"detected {len(community_map.edges())} cooccur relationships")
    log.write(f"[cooccur] {len(community_map.edges())} cooccur relationships\n")
    print(f"detected {len(community_map.nodes)} community api nodes")
    log.write(f"[community nodes] {len(community_map.nodes)} community api nodes\n")
    print("dumping community map")
    nx.write_gexf(
        community_map, f"{base_dir}/data/exp/community_map_thresold_{COMMUNITY_THRESHOLD}.gexf")
    # 20210310：决定先不向 concept map写入community关系了，反正信息都到community map里了


if __name__ == "__main__":
    log = open(f"{base_dir}/data/exp/MENIA_log.log", 'w', encoding='utf-8')
    freqs = EXP_COMMUNITY_FREQUENCY_THRESHOLDS
    for freq in freqs:
        add_community_rel_heuristic_1(JAVADOC_GLOBAL_NAME, freq, log)
    log.close()
