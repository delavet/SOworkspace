import json

from tqdm import tqdm
from collections import OrderedDict
from util.community_info.api_info_center import APIinfoCenter
from util.community_info.so_thread_info_center import ThreadInfoCenter
from util.config import COMMUNITY_RECORD_STORE_PATH, JAVADOC_GLOBAL_NAME, COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH

'''
基于社区发现和图嵌入，最终使用启发式方法向学习者推荐
20210313使用的启发式想法：
第一部分：基础API的学习推荐
在图谱中degree极大，community frequency很大
第二部分：一般API的学习推荐
学习的内容就是post，所以就是给用户推荐一系列的thread
起点thread的推荐：
	1. API图谱做图嵌入
		a. 想法一：直接在社区中寻找关系最为密切的一对API为起点
		b. 想法二：先寻找社区频率高的、度比较大的API，再寻找与他关系最为密切的API作为一对（先尝试这个想法）
	2. 遍历同时提到这两个API的所有帖子，寻找满足以下启发式条件的帖子作为起点：
		a. 最好包含how to
		b. Score、ViewCount、FavoriteCount综合最高
路径上thread的推荐：
	不断推荐当前api出现的帖子，有别的api出现就作为下一个备选，在备选中选择距离最近的api作为下一个推荐内容
'''


def get_recommend_entry_api(api_community: list, info_center: APIinfoCenter):
    if len(api_community) <= 1:
        return None
    api_community_with_score = [
        (api, info_center.get_api_community_score(api)) for api in api_community]
    sorted_api_community_with_score = sorted(
        api_community_with_score, reverse=True, key=lambda s: s[1])
    return sorted_api_community_with_score[0][0]


def recommend_learn_entry_threads(api_community: list, doc_name: str, api_info_center, thread_info_center):
    '''
    现在的做法没有加入图嵌入的API亲密关系推断，而是只是推荐
    # Return
    返回推荐在此社区中学习的首个帖子的id
    '''
    recommend_learn_entry_api = get_recommend_entry_api(
        api_community, api_info_center)
    candidate_thread_ids = api_info_center.get_related_thread_ids(
        recommend_learn_entry_api)
    recommended_thread_with_scores = thread_info_center.resort_thread_by_recommend_score(
        candidate_thread_ids)
    return recommended_thread_with_scores[0][0]["Id"]


def recommend_learn_entry_thread_for_each_community(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(COMMUNITY_RECORD_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_communities = dict(json.load(rf))
    recommend_result = OrderedDict()
    api_info_center = APIinfoCenter(doc_name)
    thread_info_center = ThreadInfoCenter(doc_name)
    for community_id, api_community in tqdm(api_communities.items()):
        recommend_result[community_id] = recommend_learn_entry_threads(
            api_community, doc_name, api_info_center, thread_info_center)
    with open(COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(recommend_result, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    recommend_learn_entry_thread_for_each_community(JAVADOC_GLOBAL_NAME)
