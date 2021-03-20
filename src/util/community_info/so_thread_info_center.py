import os
import json
import pickle
from typing import Tuple

from ..config import SO_POSTS_SEGMENT_INFO_STORE_PATH, JAVADOC_GLOBAL_NAME, SO_POSTS_STORE_PATH, DOC_NAME_TO_SO_TAG
from ..utils import normalize

# ThreadInfoCenter的推荐策略
strategy_heuristic = 'heuristic'
strategy_AHP = 'AHP'


class ThreadInfoCenter:

    def __init__(self, doc_name: str = JAVADOC_GLOBAL_NAME, strategy=strategy_heuristic) -> None:
        self.doc_name = doc_name
        self.strategy = strategy
        with open(SO_POSTS_SEGMENT_INFO_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.thread_segment_info = dict(json.load(rf))

    def batch_get_thread_detail_info(self, thread_id_batch: list):
        '''
        成批的从文件中读取thread信息，最大化IO效率
        '''
        if len(thread_id_batch) == 0:
            return []
        ret = []
        segment_info_list = sorted([[str(thread_id), self.thread_segment_info[str(thread_id)][0], self.thread_segment_info[str(thread_id)][1]]
                                    for thread_id in thread_id_batch], key=lambda s: s[1])
        cur_filename = segment_info_list[0][1]
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[self.doc_name]], cur_filename), 'rb') as rbf:
            cur_partial_threads = list(pickle.load(rbf))
        for segment_info in segment_info_list:
            if segment_info[1] != cur_filename:
                cur_filename = segment_info[1]
                with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[self.doc_name]], cur_filename), 'rb') as rbf:
                    cur_partial_threads = list(pickle.load(rbf))
            detail_thread = cur_partial_threads[segment_info[2]]
            ret.append(detail_thread)
        return ret

    def batch_get_thread_concise_info(self, thread_id_batch: list):
        '''
        成批的从文件中读取thread信息，最大化IO效率，只获取id、title和tags
        '''
        if len(thread_id_batch) == 0:
            return []
        ret = []
        segment_info_list = sorted([[str(thread_id), self.thread_segment_info[str(thread_id)][0], self.thread_segment_info[str(thread_id)][1]]
                                    for thread_id in thread_id_batch], key=lambda s: s[1])
        cur_filename = segment_info_list[0][1]
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[self.doc_name]], cur_filename), 'rb') as rbf:
            cur_partial_threads = list(pickle.load(rbf))
        for segment_info in segment_info_list:
            if segment_info[1] != cur_filename:
                cur_filename = segment_info[1]
                with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[self.doc_name]], cur_filename), 'rb') as rbf:
                    cur_partial_threads = list(pickle.load(rbf))
            detail_thread = cur_partial_threads[segment_info[2]]
            ret.append({
                'Id': detail_thread['Id'],
                'Title': detail_thread["Title"],
                'Tags': detail_thread['Tags']
            })
        return ret
    
    def get_thread_detail_info(self, thread_id):
        segment_info = self.thread_segment_info.get(str(thread_id), None)
        if segment_info is None:
            return None
        ret = None
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[self.doc_name]], segment_info[0]), 'rb') as rbf:
            partial_threads = pickle.load(rbf)
            ret = partial_threads[segment_info[1]]
        return ret

    def get_thread_recommend_score_heuristic(self, thread_info: dict):
        '''
        获取一个thread的推荐分数，从以下几个角度考虑：
        1. ViewCount，0.1
        2. Score，0.4
        3. FavoriteCount，0.3
        4. post里是否包含how to，0.2

        ## return
        返回一个thread的推荐分数
        '''
        view_count = normalize(
            thread_info.get("ViewCount", 0) / 100)  # 感觉ViewCount实在太大了，给他改小点
        thread_score = normalize(thread_info.get("Score", 0))
        favorite_count = normalize(thread_info.get("FavoriteCount", 0))
        how_to_score = 0
        if 'how' in thread_info["Title"].lower():
            how_to_score = 1
        elif 'how' in thread_info["Body"].lower():
            how_to_score = 0.4
        return 0.1*view_count + 0.4*thread_score + 0.3*favorite_count + 0.2*how_to_score

    def get_thread_recommend_score(self, thread_info: dict):
        if self.strategy == strategy_heuristic:
            return self.get_thread_recommend_score_heuristic(thread_info)
        else:
            # 需要增加AHP的策略方法，现在两个分支都用的一个方法
            return self.get_thread_recommend_score_heuristic(thread_info)

    def resort_thread_by_recommend_score(self, thread_id_list: list):
        '''
        ## return
        [(thread_detail_info, thread_score), ...]

        一个tuple的列表，tuple的第一项是thread的所有详细信息（dict格式），第二项是thread的推荐得分

        # 一定要注意返回的格式发生了变化！！不再只是thread id的列表了
        '''
        detail_threads = self.batch_get_thread_detail_info(thread_id_list)
        thread_with_score = sorted(
            [(thread, self.get_thread_recommend_score(thread)) for thread in detail_threads], key=lambda s: s[1], reverse=True)
        return thread_with_score
