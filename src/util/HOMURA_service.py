import os
import json
import networkx as nx

from util.constant import *

from .utils import get_api_name_from_entity_id
from .config import HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH, COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH, API_THREAD_ID_MAP_STORE_PATH
from .concept_map.common import get_latest_concept_map, get_latest_community_map


class HOMURAservice:
    def __init__(self, doc_name):
        self.api_recommend_constraint = 5
        with open(HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.community_api_recommend = json.load(rf)
            self.community_ids = list(self.community_api_recommend.keys())
        with open(COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf2:
            self.community_thread_id_recommend = json.load(rf2)
        with open(API_THREAD_ID_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf3:
            self.API_thread_id_map = json.load(rf3)
        self.community_map = get_latest_community_map()
        self.concept_map = get_latest_concept_map()
        i = 0
        self.id2APIname = {}
        self.APIname2id = {}
        for node in self.concept_map.nodes:
            self.id2APIname[str(i)] = node  # 因为URL问题不得不把node name转换成数字id
            self.APIname2id[node] = str(i)
            i += 1
        
        
    
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
            "apis": [get_api_name_from_entity_id(api) for api in recommended_apis],
            "thread_info": recommended_thread
        }
        return ret

    
    def get_community_submap_by_api(self, api_id, section_id = None):
        '''
        根据API名返回需要渲染的COMMUNITY MAP的子图
        '''
        api_name = self.id2APIname[str(api_id)]
        if api_name not in self.community_map.nodes:
            return {
                'nodes': [],
                'edges': []
            }
        submap_nodes = list(nx.dfs_postorder_nodes(
            self.community_map, api_name, depth_limit=3))
        if section_id is not None:
            section_apis = self.community_api_recommend.get(section_id, [])
            submap_nodes = [node for node in submap_nodes if node in section_apis]
        subgraph = nx.subgraph(self.community_map, submap_nodes)
        nodes = []
        edges = []
        for node in subgraph.nodes:
            node_data = {
                'id': self.APIname2id[node], 
                'label': subgraph.nodes[node][NodeAttributes.NAME],
                'apiName': node,
                'apiShortName': get_api_name_from_entity_id(node),
                'Ntype': subgraph.nodes[node][NodeAttributes.Ntype],
                'desctiption': subgraph.nodes[node][NodeAttributes.DESCRIPTION],
                'isCenter': self.APIname2id[node] == api_id,
                'type': 'APInode'
            }
            nodes.append(node_data)
        for source, target in subgraph.edges():
            edge_data = {
                'source': self.APIname2id[source],
                'target': self.APIname2id[target],
                'label': subgraph[source][target][EdgeAttrbutes.Etype],
                'relatedThreads': subgraph[source][target][EdgeAttrbutes.COOCCUR_THREADS]
            }
            edges.append(edge_data)
        return {
            'nodes': nodes,
            'edges': edges
        }

    def get_community_submap_by_section(self, section_id):
        '''
        根据section返回需要推荐的API子图
        '''
        recommend_API_id = self.APIname2id[self.community_api_recommend[str(
            section_id)][0]]
        return self.get_community_submap_by_api(recommend_API_id, section_id)
