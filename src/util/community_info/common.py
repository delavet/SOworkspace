import os
import re
import json
import pickle

from util.config import APIDOC_API_URL_REGEX_PATTERN, MENIA_WHOLE_PREDICTION_STORE_PATH, SO_POSTS_STORE_PATH, DOC_NAME_TO_SO_TAG, JAVADOC_GLOBAL_NAME
from util.nel.candidate_select import get_gt_candidate
from util.utils import get_api_qualified_name_from_entity_id
from tqdm import tqdm


def detect_API_counts(all_predictions: dict):
    total_count = sum([len(item)
                       for item in all_predictions.values()])
    print(f"{total_count} of the APIs predicted")


def extend_thread2api_detection_result_with_ground_truth(doc_name: str):
    '''
    利用SO thread中天然的超链接，将检测出的thread与API的对应联系进行丰富
    '''
    with open(MENIA_WHOLE_PREDICTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        all_predictions = dict(json.load(rf))
    post_filenames = os.listdir(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]])
    for filename in post_filenames:
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]], filename), "rb") as rbf:
            partial_threads = list(pickle.load(rbf))
        for thread in tqdm(partial_threads):
            links = thread.get("Links", [])
            apidoc_links = [link for link in links if re.search(
                APIDOC_API_URL_REGEX_PATTERN[JAVADOC_GLOBAL_NAME], str(link)) is not None]
            api_map = {}
            for apidoc_link in apidoc_links:
                api = get_gt_candidate(apidoc_link)
                if api is None:
                    continue
                api_map[apidoc_link] = api
            if len(api_map) == 0:
                continue
            thread_id = str(thread["Id"])
            if thread_id not in all_predictions.keys():
                all_predictions[thread_id] = {}
            for apidoc_link, api in api_map.items():
                if api in all_predictions[thread_id].values():
                    continue
                all_predictions[thread_id][apidoc_link] = api
    with open(MENIA_WHOLE_PREDICTION_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        detect_API_counts(all_predictions)
        json.dump(all_predictions, wf, indent=2, ensure_ascii=False)
                
