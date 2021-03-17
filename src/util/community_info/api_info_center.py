import json
import os
import networkx as nx

from ..config import COMMUNITY_FREQUENCY_STORE_PATH, JAVADOC_GLOBAL_NAME, LATEST_COMMUNITY_MAP_PATH, MENIA_WHOLE_PREDICTION_STORE_PATH
from ..utils import normalize


class APIinfoCenter:
    def __init__(self, doc_name: str = JAVADOC_GLOBAL_NAME) -> None:
        self.community_frequency_ratio = 0.3
        self.community_degree_ratio = 0.7
        with open(COMMUNITY_FREQUENCY_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.community_frequency = dict(json.load(rf))
        self.community_map = nx.read_gexf(LATEST_COMMUNITY_MAP_PATH[doc_name])
        with open(MENIA_WHOLE_PREDICTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.thread2api = dict(json.load(rf))
            self.api2thread = {}
            for thread_id, mention2api in self.thread2api.items():
                apis = list(mention2api.values())
                for api in apis:
                    if api not in self.api2thread.keys():
                        self.api2thread[api] = []
                    self.api2thread[api].append(str(thread_id))

    def get_communtiy_frequency(self, api: str) -> int:
        if api not in self.community_frequency.keys():
            return -1
        return self.community_frequency[api]

    def get_degree_in_community(self, api: str) -> int:
        if api not in self.community_map.nodes:
            return -1
        return len(self.community_map.adj[api])

    def get_api_community_score(self, api: str):
        return self.community_frequency_ratio*normalize(self.get_communtiy_frequency(api)) + self.community_degree_ratio*normalize(self.get_degree_in_community(api))

    def get_related_thread_ids(self, api: str):
        if api not in self.api2thread.keys():
            return []
        return self.api2thread[api]