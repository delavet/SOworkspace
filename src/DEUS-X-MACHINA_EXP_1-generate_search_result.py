import json
import os

from tqdm import tqdm
from util.config import JAVADOC_GLOBAL_NAME, EXP_DEUS_X_MACHINA_CONCEPT_SEARCH_RESULT_STORE_PATH, EXP_DEUX_X_MACHINA_ANS_STORE_PATH, EXP_DEUX_X_MACHINA_ANS2_STORE_PATH,EXP_DEUS_X_MACHINA_LITERAL_STRICT_SEARCH_RESULT_STORE_PATH, EXP_DEUX_X_MACHINA_LITERAL_SEARCH_RESULT_STORE_PATH, base_dir
from util.apidoc_search.api_search_service import ApiSearchService
from util.community_info.so_thread_info_center import ThreadInfoCenter
from util.nel.candidate_select import get_gt_candidate
from util.utils import turn_to_class_level_api, MRR


def search_exp(service: ApiSearchService, search_mode: str, store_path: str, thread_details: list, log):
    print(f'=====search mode: {search_mode}=====')
    log.write(f'=====search mode: {search_mode}=====\n')
    hit_in_5 = 0
    hit_in_10 = 0
    hit_in_20 = 0
    hit_in_30 = 0
    hit_in_50 = 0
    hit_indexes = []
    search_records = []
    failed_to_find_gt = 0
    for thread in tqdm(thread_details):
        title = thread['Title']
        links = thread['Links']
        gt_apis = [get_gt_candidate(link) for link in links if get_gt_candidate(link) is not None]
        gt_classes = set([turn_to_class_level_api(api) for api in gt_apis])
        record = {
            'query': title,
            'groundtruth': list(gt_classes)
        }
        if len(gt_classes) == 0:
            failed_to_find_gt += 1
            continue
        search_results = [item[0] for item in service.search(search_mode, title)]
        record['result'] = search_results
        hit_index = -1
        for i, api in enumerate(search_results):
            if api not in gt_classes:
                continue
            hit_index = i + 1
            if i < 5:
                hit_in_5 += 1
            if i < 10:
                hit_in_10 += 1
            if i < 20:
                hit_in_20 += 1
            if i < 30:
                hit_in_30 += 1
            if i < 50:
                hit_in_50 += 1
        hit_indexes.append(hit_index)
        search_records.append(record)
    total_count = len(search_records)
    print(f'failed to find ground truth for {failed_to_find_gt} cases')
    print(f'hit in 5: {hit_in_5} of {total_count}')
    log.write(f'hit in 5: {hit_in_5} of {total_count}\n')
    print(f'hit in 10: {hit_in_10} of {total_count}')
    log.write(f'hit in 10: {hit_in_10} of {total_count}\n')
    print(f'hit in 20: {hit_in_20} of {total_count}')
    log.write(f'hit in 20: {hit_in_20} of {total_count}\n')
    print(f'hit in 30: {hit_in_30} of {total_count}')
    log.write(f'hit in 30: {hit_in_30} of {total_count}\n')
    print(f'hit in 50: {hit_in_50} of {total_count}')
    log.write(f'hit in 50: {hit_in_50} of {total_count}\n')
    mrr = MRR(hit_indexes)
    print(f'mrr: {mrr}')
    log.write(f'mrr: {mrr}\n')
    with open(store_path, 'w', encoding='utf-8') as wf:
        json.dump(search_records, wf, indent=2, ensure_ascii=False)
    

def DXM_exp(doc_name: str):
    service = ApiSearchService(doc_name)
    thread_info_center = ThreadInfoCenter(doc_name)
    with open(EXP_DEUX_X_MACHINA_ANS_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        thread_ids = [str(ans["Id"]) for ans in json.load(rf)]
    with open(EXP_DEUX_X_MACHINA_ANS2_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf2:
        thread_ids2 = [str(ans["Id"]) for ans in json.load(rf2)]
    thread_ids.extend(thread_ids2) # 视情况去掉thread_id2
    threads = thread_info_center.batch_get_thread_detail_info(thread_ids)
    thresholds = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for th in thresholds:
        with open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_concept_thres_{th}.log', 'w', encoding='utf-8') as rf_log:
            service.set_concept_search_threshold(th)
            print('===== testing concept searching for threshold ', th)
            search_exp(service, 'concept',
                    EXP_DEUS_X_MACHINA_CONCEPT_SEARCH_RESULT_STORE_PATH[doc_name], threads, rf_log)
    with open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_literal.log', 'w', encoding='utf-8') as rf_log:
        search_exp(service, 'literal',
                   EXP_DEUX_X_MACHINA_LITERAL_SEARCH_RESULT_STORE_PATH[doc_name], threads, rf_log)
    with open(f'{base_dir}/data/exp/DEUS-X-MACHINA-EXP/log_literal_strict.log', 'w', encoding='utf-8') as rf_log:
        search_exp(service, 'literal_strict',
                   EXP_DEUS_X_MACHINA_LITERAL_STRICT_SEARCH_RESULT_STORE_PATH[doc_name], threads, rf_log)


if __name__ == "__main__":
    DXM_exp(JAVADOC_GLOBAL_NAME)
