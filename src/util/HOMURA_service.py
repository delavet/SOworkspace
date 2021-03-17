import os
import json
from .config import HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH, COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH


class HOMURAservice:
    def __init__(self, doc_name):
        self.api_recommend_constraint = 5
        with open(HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.community_api_recommend = json.load(rf)
            self.community_ids = list(self.community_api_recommend.keys())
        with open(COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf2:
            self.community_thread_id_recommend = json.load(rf2)
    
    def get_community_recommend_info(self, community_id):
        '''
        获取一个社群的概要推荐信息
        包括：社群内比较代表性的API和一个代表性的thread的信息
        '''
        community_id = str(community_id)
        recommended_apis = self.community_api_recommend.get(community_id, [])
        if len(recommended_apis) > self.api_recommend_constraint:
            recommended_apis = recommended_apis[:self.api_recommend_constraint]
        recommended_thread = self.community_thread_id_recommend.get(community_id, {"Id": 0, "Title": "", "Tags": ""})
        ret = {
            "section_id": community_id,
            "apis": recommended_apis,
            "thread_info": recommended_thread
        }
        return ret

