import json

from tqdm import tqdm
from collections import OrderedDict
from util.community_info.api_info_center import APIinfoCenter
from util.community_info.so_thread_info_center import ThreadInfoCenter
from util.config import COMMUNITY_RECORD_STORE_PATH, JAVADOC_GLOBAL_NAME, HOMURA_COMMUNITY_TAGS_RECOMMEND_STORE_PATH, API_THREAD_ID_MAP_STORE_PATH

'''
HOMURA系统中为了更好展示每个学习section的内容概况
分析生成了每个社群对应出现频率最高的几个tag
方便用户决策学习哪个
'''


def get_tag_recommend_list(api_community: list, info_center: ThreadInfoCenter, api_thread_id_map: dict) -> list:
    if len(api_community) <= 1:
        return None
    related_thread_ids = set()
    for api in api_community:
        related_thread_ids.update(api_thread_id_map.get(api, []))
    related_threads = info_center.batch_get_thread_detail_info(
        list(related_thread_ids))
    tag_count_map = {}
    for thread in related_threads:
        tags = thread['Tags'].strip('<').strip('>').split('><')
        for tag in tags:
            if tag == 'java':
                continue
            tag_count_map[tag] = tag_count_map.get(tag, 0) + 1
    sorted_tags = [item[0] for item in sorted(
        list(tag_count_map.items()), key=lambda x: x[1], reverse=True)]
    if len(sorted_tags) > 10:
        return sorted_tags[:10]
    else:
        return sorted_tags


def recommend_tags_for_each_community(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(API_THREAD_ID_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf_api:
        api_thread_map = json.load(rf_api)
    with open(COMMUNITY_RECORD_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_communities = dict(json.load(rf))
    recommend_result = OrderedDict()
    thread_info_center = ThreadInfoCenter(doc_name)
    for community_id, api_community in tqdm(list(api_communities.items())):
        recommend_result[community_id] = get_tag_recommend_list(
            api_community, thread_info_center, api_thread_map)
    with open(HOMURA_COMMUNITY_TAGS_RECOMMEND_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(recommend_result, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    recommend_tags_for_each_community(JAVADOC_GLOBAL_NAME)
