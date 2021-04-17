import os
import json
from types import CodeType
import networkx as nx

from util.constant import *

from .utils import get_api_name_from_entity_id
from .config import HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH, COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH, API_THREAD_ID_MAP_STORE_PATH, APIDOC_DESCRIPTION_STORE_PATH, HOMURA_COMMUNITY_TAGS_RECOMMEND_STORE_PATH
from .concept_map.common import get_latest_concept_map, get_latest_community_map
# from .mysql_access.posts import DBPosts
from .community_info.so_thread_info_center import ThreadInfoCenter


class HOMURAservice:
    def __init__(self, doc_name):
        # self.post_db = DBPosts()
        self.thread_info_center = ThreadInfoCenter(doc_name)
        self.api_recommend_constraint = 5
        with open(HOMURA_COMMUNITY_API_RECOMMEND_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
            self.community_api_recommend = json.load(rf)
            self.community_ids = list(self.community_api_recommend.keys())
        with open(HOMURA_COMMUNITY_TAGS_RECOMMEND_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf1:
            self.community_tags_recommend = json.load(rf1)
        with open(COMMUNITY_RECOMMEND_ENTRY_THREADS_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf2:
            self.community_thread_id_recommend = json.load(rf2)
        with open(API_THREAD_ID_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf3:
            self.API_thread_id_map = json.load(rf3)
        with open(APIDOC_DESCRIPTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf4:
            self.api_doc_descriptions = json.load(rf4)
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
        recommended_tags = self.community_tags_recommend.get(community_id, [])
        if len(recommended_apis) > self.api_recommend_constraint:
            recommended_apis = recommended_apis[:self.api_recommend_constraint]
        recommended_thread = self.community_thread_id_recommend.get(
            community_id, {"Id": 0, "Title": "", "Tags": ""})
        ret = {
            "section_id": community_id,
            "apis": [get_api_name_from_entity_id(api) for api in recommended_apis],
            "thread_info": recommended_thread,
            "tags": recommended_tags
        }
        return ret

    def get_community_submap_by_api(self, api_id, section_id=None):
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
            self.community_map, api_name, depth_limit=4))
        if section_id is not None:
            section_apis = self.community_api_recommend.get(section_id, [])
            submap_nodes = [
                node for node in submap_nodes if node in section_apis]
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
                'type': 'image'
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

    def get_concept_submap_by_api(self, api_id):
        api_name = self.id2APIname[str(api_id)]
        if api_name not in self.community_map.nodes:
            return {
                'nodes': [],
                'edges': []
            }
        nodes = []
        edges = []
        edge_hash = set()
        node_hash = set()
        temp_node = api_name
        class_node = None
        success = True
        round_counter = 0
        while success and round_counter < 6:
            success = False
            if self.concept_map.nodes[temp_node][NodeAttributes.Ntype] in class_level_node_types:
                class_node = temp_node
            for pred in self.concept_map.predecessors(temp_node):
                if self.concept_map[pred][temp_node][EdgeAttrbutes.Etype] == EdgeType.INCLUDE:
                    success = True
                    edges.append({
                        'source': self.APIname2id[pred],
                        'target': self.APIname2id[temp_node],
                        'label': self.concept_map[pred][temp_node][EdgeAttrbutes.Etype],
                        'style': {
                            'endArrow': True
                        }
                    })
                    edge_hash.add(
                        f'{pred}_{temp_node}')
                    nodes.append({
                        'id': self.APIname2id[temp_node],
                        'label': self.concept_map.nodes[temp_node].get(NodeAttributes.NAME, 'no_name'),
                        'apiName': temp_node,
                        'apiShortName': get_api_name_from_entity_id(temp_node),
                        'Ntype': self.concept_map.nodes[temp_node].get(NodeAttributes.Ntype, 'no type!'),
                        'desctiption': self.concept_map.nodes[temp_node].get(NodeAttributes.DESCRIPTION, 'no description'),
                        'isCenter': self.APIname2id[temp_node] == api_id,
                        'type': 'image'
                    })
                    node_hash.add(temp_node)
                    temp_node = pred
                    round_counter += 1
                    break
        if class_node is not None:
            submap_nodes = [node for node in nx.dfs_postorder_nodes(
                self.concept_map, api_name, depth_limit=5) if self.concept_map.nodes[node].get(NodeAttributes.Ntype, '') not in field_level_node_types]
            subgraph = nx.subgraph(self.concept_map, submap_nodes)
            for node in subgraph.nodes:
                if node in node_hash or NodeAttributes.Ntype not in subgraph.nodes[node].keys():
                    continue
                node_hash.add(node)
                node_data = {
                    'id': self.APIname2id[node],
                    'label': subgraph.nodes[node].get(NodeAttributes.NAME, 'no_name'),
                    'apiName': node,
                    'apiShortName': get_api_name_from_entity_id(node),
                    'Ntype': subgraph.nodes[node][NodeAttributes.Ntype],
                    'desctiption': subgraph.nodes[node].get(NodeAttributes.DESCRIPTION, 'no description'),
                    'isCenter': self.APIname2id[node] == api_id,
                    'type': 'image'
                }
                nodes.append(node_data)
            for source, target in subgraph.edges():
                if f'{source}_{target}' in edge_hash or source not in node_hash or target not in node_hash:
                    continue
                edge_hash.add(f'{source}_{target}')
                edge_data = {
                    'source': self.APIname2id[source],
                    'target': self.APIname2id[target],
                    'label': subgraph[source][target][EdgeAttrbutes.Etype],
                    'style': {
                        'endArrow': True
                    }
                }
                edges.append(edge_data)
        return {
            'nodes': nodes,
            'edges': edges
        }

    def get_api_description_html(self, api_id):
        '''
        根据提供的API找到对应的描述html
        '''
        api_name = self.id2APIname[api_id]
        return get_api_name_from_entity_id(api_name), self.api_doc_descriptions.get(api_name, '<div></div>')

    '''
    def get_thread_infos_by_api(self, api_id, page, limit):
        
        # 没做推荐，直接把post一股脑的甩给他了
        
        api_name = self.id2APIname[api_id]
        thread_ids = self.API_thread_id_map[api_name]
        start = page * limit
        if start >= len(thread_ids):
            return []
        end = min(len(thread_ids) - 1, (page + 1) * limit)
        query = ','.join(thread_ids[start:end])
        ret = self.post_db.get_thread_info_by_ids(query)
        return ret
    '''

    def get_thread_infos_by_api_local(self, api_id, page, limit):
        '''
        用本地文件拿数据，在服务器太拉胯的时候用
        '''
        api_name = self.id2APIname[api_id]
        thread_ids = self.API_thread_id_map[api_name]
        start = page * limit
        if start >= len(thread_ids):
            return []
        end = min(len(thread_ids) - 1, (page + 1) * limit)
        id_batch = thread_ids[start: end]
        ret = self.thread_info_center.batch_get_thread_concise_info(id_batch)
        return ret

    def get_thread_infos_by_thread_ids_local(self, thread_ids, page, limit):
        '''
        用本地文件拿数据，在服务器太拉胯的时候用
        '''
        start = page * limit
        if start >= len(thread_ids):
            return []
        end = min(len(thread_ids) - 1, (page + 1) * limit)
        id_batch = thread_ids[start: end]
        ret = self.thread_info_center.batch_get_thread_concise_info(id_batch)
        return ret

    def get_thread_html(self, thread_id):
        '''
        获取一个thread的原始html和title
        '''
        thread_detail_info = self.thread_info_center.get_thread_detail_info(
            thread_id)
        answers = thread_detail_info['Answers']
        bodys = [thread_detail_info['Body']]
        bodys.extend([answer['Body'] for answer in answers])
        ret = {
            'title': thread_detail_info['Title'],
            'html': '<hr/>'.join(bodys)
        }
        return ret

    def get_api_id_short_description(self, api_name):
        return self.APIname2id[api_name], self.concept_map.nodes[api_name].get(NodeAttributes.DESCRIPTION, '')
