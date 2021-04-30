import json
import sys
import numpy as np
import networkx as nx

from tqdm import tqdm
from util.config import JAVADOC_GLOBAL_NAME, EXP_DEUS_X_MACHINA_CONCEPT_SEARCH_RESULT_STORE_PATH, EXP_DEUS_X_MACHINA_LITERAL_STRICT_SEARCH_RESULT_STORE_PATH,EXP_DEUX_X_MACHINA_LITERAL_SEARCH_RESULT_STORE_PATH, base_dir
from util.concept_map.common import get_latest_concept_map
from util.constant import *


def concept_map_shortest_path(concept_map, api1: str, api2: str):
    ret = sys.maxsize
    try:
        l1 = nx.shortest_path_length(concept_map, api1, api2)
        ret = min(ret, l1)
    except:
        pass
    try:
        l2 = nx.shortest_path_length(concept_map, api2, api1)
        ret = min(ret, l2)
    except:
        pass
    return ret



def exp_shortest_paths(concept_map, search_result_records, log):
    l5s = []
    l10s = []
    l20s = []
    l30s = []
    l50s = []
    whole_avg_l = []
    total_unreachable_case_numbers = []
    usable_search_result_counts = []
    for record in tqdm(search_result_records):
        ground_truth = record['groundtruth'][0]
        results = record['result']
        shortest_path_top_5 = sys.maxsize
        shortest_path_top_10 = sys.maxsize
        shortest_path_top_20 = sys.maxsize
        shortest_path_top_30 = sys.maxsize
        shortest_path_top_50 = sys.maxsize
        path_lengths = []
        unreachable_count = 0
        usable_search_result_count = 0
        for i, result_api in enumerate(results):
            path_length = concept_map_shortest_path(
                concept_map, result_api, ground_truth)
            if path_length == sys.maxsize:
                unreachable_count += 1
            else:
                path_lengths.append(path_length) 
            if i < 5:
                shortest_path_top_5 = min(path_length, shortest_path_top_5)
            if i < 10:
                shortest_path_top_10 = min(path_length, shortest_path_top_10)
                if path_length <= 2:
                    usable_search_result_count += 1
            if i < 20:
                shortest_path_top_20 = min(path_length, shortest_path_top_20)
            if i < 30:
                shortest_path_top_30 = min(path_length, shortest_path_top_30)
            if i < 50:
                shortest_path_top_50 = min(path_length, shortest_path_top_50)
        l5s.append(shortest_path_top_5)
        l10s.append(shortest_path_top_10)
        l20s.append(shortest_path_top_20)
        l30s.append(shortest_path_top_30)
        l50s.append(shortest_path_top_50)
        total_unreachable_case_numbers.append(unreachable_count)
        usable_search_result_counts.append(usable_search_result_count)
        query = record.get('query', '')
        print(f'##{i} -- query: {query}')
        log.write(f'## query: {query}\n')
        print(f'shortest path found in top 5: {shortest_path_top_5}')
        log.write(f'shortest path found in top 5: {shortest_path_top_5}\n')
        print(f'shortest path found in top 10: {shortest_path_top_10}')
        log.write(f'shortest path found in top 10: {shortest_path_top_10}\n')
        print(f'shortest path found in top 20: {shortest_path_top_20}')
        log.write(f'shortest path found in top 20: {shortest_path_top_20}\n')
        print(f'shortest path found in top 30: {shortest_path_top_30}')
        log.write(f'shortest path found in top 30: {shortest_path_top_30}\n')
        print(f'shortest path found in top 50: {shortest_path_top_50}')
        log.write(f'shortest path found in top 50: {shortest_path_top_50}\n')
        avg_path_length = np.mean(path_lengths)
        whole_avg_l.append(avg_path_length)
        print(f'average length of the apis searched to ground-truth: {avg_path_length}')
        log.write(
            f'average length of the apis searched to ground-truth: {avg_path_length}\n')
        print(f'number of learning entry which could be used in top 10: {usable_search_result_count}')
        log.write(
            f'number of learning entry which could be used in top 10: {usable_search_result_count}\n')
    print('=====SUMMARIZATION=====')
    log.write('=====SUMMARIZATION=====\n')
    unreachable_5 = len([l for l in l5s if l == sys.maxsize])
    print(f'number of unreachable cases in top 5 recommend: {unreachable_5}')
    log.write(
        f'number of unreachable cases in top 5 recommend: {unreachable_5}\n')
    l5s = [l for l in l5s if l < sys.maxsize]
    shortest_path_top_5 = np.mean(l5s)

    unreachable_10 = len([l for l in l10s if l == sys.maxsize])
    print(f'number of unreachable cases in top 10 recommend: {unreachable_10}')
    log.write(
        f'number of unreachable cases in top 10 recommend: {unreachable_10}\n')
    l10s = [l for l in l10s if l < sys.maxsize]
    shortest_path_top_10 = np.mean(l10s)

    unreachable_20 = len([l for l in l20s if l == sys.maxsize])
    print(f'number of unreachable cases in top 20 recommend: {unreachable_20}')
    log.write(
        f'number of unreachable cases in top 20 recommend: {unreachable_20}\n')
    l20s = [l for l in l20s if l < sys.maxsize]
    shortest_path_top_20 = np.mean(l20s)

    unreachable_30 = len([l for l in l30s if l == sys.maxsize])
    print(f'number of unreachable cases in top 30 recommend: {unreachable_30}')
    log.write(
        f'number of unreachable cases in top 30 recommend: {unreachable_30}\n')
    l30s = [l for l in l30s if l < sys.maxsize]
    shortest_path_top_30 = np.mean(l30s)

    unreachable_50 = len([l for l in l50s if l == sys.maxsize])
    print(f'number of unreachable cases in top 50 recommend: {unreachable_50}')
    log.write(
        f'number of unreachable cases in top 50 recommend: {unreachable_50}\n')
    l50s = [l for l in l50s if l < sys.maxsize]
    shortest_path_top_50 = np.mean(l50s)
    print(f'average shortest path found in top 5: {shortest_path_top_5}')
    log.write(f'average shortest path found in top 5: {shortest_path_top_5}\n')
    print(f'average shortest path found in top 10: {shortest_path_top_10}')
    log.write(
        f'average shortest path found in top 10: {shortest_path_top_10}\n')
    print(f'average shortest path found in top 20: {shortest_path_top_20}')
    log.write(
        f'average shortest path found in top 20: {shortest_path_top_20}\n')
    print(f'average shortest path found in top 30: {shortest_path_top_30}')
    log.write(
        f'average shortest path found in top 30: {shortest_path_top_30}\n')
    print(f'average shortest path found in top 50: {shortest_path_top_50}')
    log.write(
        f'average shortest path found in top 50: {shortest_path_top_50}\n')
    avg_unreachable_count = np.mean(total_unreachable_case_numbers)
    print(
        f'whole average unreachable searched apis: {avg_unreachable_count} apis')
    log.write(
        f'whole average unreachable searched apis: {avg_unreachable_count} apis\n')
    avg_path_length = np.mean([l for l in whole_avg_l if not np.isnan(l)])
    print(
        f'whole average length of the apis searched to ground-truth: {avg_path_length}')
    log.write(
        f'whole average length of the apis searched to ground-truth: {avg_path_length}\n')
    avg_usable_count = np.mean(usable_search_result_counts)
    print(f'average usable search result in top 10: {avg_usable_count}')
    log.write(
        f'average usable search result in top 10: {avg_usable_count}\n'
    )
    

def DXM_exp_path_length(doc_name: str):
    concept_map = nx.Graph(get_latest_concept_map(doc_name))
    nodes = list(concept_map.nodes)
    for node in nodes:
        if 'java/lang/Object.html' in node:
            concept_map.remove_node(node)
            continue
        ntype = concept_map.nodes[node].get(NodeAttributes.Ntype, None)
        if ntype is None or ntype in high_level_node_types:
            concept_map.remove_node(node)
    with open(EXP_DEUS_X_MACHINA_CONCEPT_SEARCH_RESULT_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf, open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_concept_path_length.log', 'w', encoding='utf-8') as wf_log:
        records = json.load(rf)
        print('---------concept_search')
        exp_shortest_paths(concept_map, records, wf_log)
    with open(EXP_DEUX_X_MACHINA_LITERAL_SEARCH_RESULT_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf, open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_literal_path_length.log', 'w', encoding='utf-8') as wf_log:
        print('---------literal_search')
        records = json.load(rf)
        exp_shortest_paths(concept_map, records, wf_log)
    with open(EXP_DEUS_X_MACHINA_LITERAL_STRICT_SEARCH_RESULT_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf, open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_literal_strict_path_length.log', 'w', encoding='utf-8') as wf_log:
        print('---------literal_strict_search')
        records = json.load(rf)
        exp_shortest_paths(concept_map, records, wf_log)


if __name__ == "__main__":
    DXM_exp_path_length(JAVADOC_GLOBAL_NAME)
