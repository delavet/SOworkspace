import json

from tqdm import tqdm
from collections import OrderedDict
from util.community_info.api_info_center import APIinfoCenter
from util.community_info.so_thread_info_center import ThreadInfoCenter
from util.config import COMMUNITY_RECORD_STORE_PATH, JAVADOC_GLOBAL_NAME, COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH, HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH
'''
HOMURA系统中为了更好展示每个学习section的内容概况，需要先生成一个数据保存每个community的代表API，方便用户决策学习哪个
'''

def get_api_recommend_list(api_community: list, info_center: APIinfoCenter):
    if len(api_community) <= 1:
        return None
    api_community_with_score = [
        (api, info_center.get_api_community_score(api)) for api in api_community]
    sorted_api_community = [item[0] for item in sorted(
        api_community_with_score, reverse=True, key=lambda s: s[1])]
    return sorted_api_community


def recommend_api_for_each_community(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(COMMUNITY_RECORD_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_communities = dict(json.load(rf))
    recommend_result = OrderedDict()
    api_info_center = APIinfoCenter(doc_name)
    for community_id, api_community in tqdm(api_communities.items()):
        recommend_result[community_id] = get_api_recommend_list(
            api_community, api_info_center)
    with open(HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(recommend_result, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    recommend_api_for_each_community(JAVADOC_GLOBAL_NAME)
