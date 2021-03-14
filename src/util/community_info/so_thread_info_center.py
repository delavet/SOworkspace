import os
import json
import pickle
from typing import Tuple

from ..config import SO_POSTS_SEGMENT_INFO_STORE_PATH, JAVADOC_GLOBAL_NAME, SO_POSTS_STORE_PATH, DOC_NAME_TO_SO_TAG
from ..utils import normalize


class ThreadInfoCenter:
    def __init__(self, doc_name: str = JAVADOC_GLOBAL_NAME) -> None:
        self.doc_name = doc_name
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

    def get_thread_recommend_score(self, thread_info: dict):
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
            thread_info["ViewCount"] / 100)  # 感觉ViewCount实在太大了，给他改小点
        thread_score = normalize(thread_info["Score"])
        favorite_count = normalize(thread_info["FavoriteCount"])
        how_to_score = 0
        if 'how' in thread_info["Title"].lower():
            how_to_score = 1
        elif 'how' in thread_info["Body"].lower():
            how_to_score = 0.4
        return 0.1*view_count + 0.4*thread_score + 0.3*favorite_count + 0.2*how_to_score

    def resort_thread_by_recommend_score(self, thread_id_list: list) -> list[Tuple]:
        '''
        ## return
        [(thread_detail_info, thread_score), ...]

        # 一定要注意返回的格式发生了变化！！不再只是thread id的列表了
        '''
        detail_threads = self.batch_get_thread_detail_info(thread_id_list)
        thread_with_score = sorted(
            [(thread, self.get_thread_recommend_score(thread)) for thread in detail_threads], key=lambda s: s[1])
        return thread_with_score
