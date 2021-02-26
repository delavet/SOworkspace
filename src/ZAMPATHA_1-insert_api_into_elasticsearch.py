import json
from collections import OrderedDict
import networkx as nx

from tqdm import tqdm
from elasticsearch import Elasticsearch
from util.concept_map.common import get_latest_concept_map
from util.config import JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, API_ELASTIC_DOC_MAP_STORE_PATH
from util.constant import NodeType, NodeAttributes


es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)


def get_qualified_api_name(node_name: str):
    ret = node_name
    if '.html' in node_name:
        ret = ret.replace('.html', '')
    if 'api/' in node_name:
        ret = ret.replace('api/', '')
    ret = ret.replace('/', ' ')
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    return ret


def insert_api_concepts_into_elasticsearch(doc_name: str = JAVADOC_GLOBAL_NAME):
    global es
    concept_map = get_latest_concept_map(doc_name)
    api_elastic_map = OrderedDict()
    index = -1
    for node in tqdm(concept_map.nodes):
        api_name = get_qualified_api_name(node)
        description = concept_map.nodes[node][NodeAttributes.DESCRIPTION] if NodeAttributes.DESCRIPTION in concept_map.nodes[node].keys(
        ) else ''
        node_type = concept_map.nodes[node][NodeAttributes.Ntype] if NodeAttributes.Ntype in concept_map.nodes[node].keys(
        ) else ''
        if node_type == '':
            continue
        desc = node_type + ' ' + api_name + ": " + description
        # 插入全是小写，这样就没有大小写问题了。。。
        doc_body = {
            'name': api_name.lower(),
            'description': desc.lower(),
            'node_name': node
        }
        index += 1
        api_elastic_map[node] = index
        es.index(index=doc_name, doc_type='api', id=index, body=doc_body)
    with open(API_ELASTIC_DOC_MAP_STORE_PATH[JAVADOC_GLOBAL_NAME], 'w', encoding='utf-8') as wf:
        json.dump(api_elastic_map, wf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    insert_api_concepts_into_elasticsearch(JAVADOC_GLOBAL_NAME)
    print('insert over, have a try for search')
    # 插入完了试一下查询
    query_body = {
        'query': {
            'match': {
                'name': {
                    'query': 'arraylist',
                    'fuzziness': 'auto'
                }
            }
        },
        'from': 0,
        'size': 20
    }
    res = es.search(index=JAVADOC_GLOBAL_NAME,
                    filter_path='hits.hits._source.node_name', body=query_body)
    print(res)
