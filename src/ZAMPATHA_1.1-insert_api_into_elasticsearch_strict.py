import json
from collections import OrderedDict
import networkx as nx
from nltk.util import pr

from tqdm import tqdm
from elasticsearch import Elasticsearch
from util.concept_map.common import get_latest_concept_map
from util.config import JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, API_ELASTIC_DOC_MAP_STORE_PATH
from util.constant import NodeType, NodeAttributes
from util.utils import get_api_extreme_short_name_from_entity_id, pre_tokenize

'''
20210413-采用ZAMPATHA 1.1对Elasticsearch进行重新插入
和ZAMPATHA 1的区别：
对ZAMPATHA的插入规则进行了更为严格的限制
对field和method，只插入方法和属性名，对类，只插入类名
大概思路是去掉 [、 (、 < 之后的内容，然后取最后一个token。。
'''

es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)


def insert_api_concepts_into_elasticsearch(doc_name: str = JAVADOC_GLOBAL_NAME):
    global es
    concept_map = get_latest_concept_map(doc_name)
    api_elastic_map = OrderedDict()
    index = -1
    for node in tqdm(concept_map.nodes):
        api_name = get_api_extreme_short_name_from_entity_id(node)
        description = concept_map.nodes[node][NodeAttributes.DESCRIPTION] if NodeAttributes.DESCRIPTION in concept_map.nodes[node].keys(
        ) else ''
        node_type = concept_map.nodes[node][NodeAttributes.Ntype] if NodeAttributes.Ntype in concept_map.nodes[node].keys(
        ) else ''
        if node_type == '':
            continue
        desc = description
        # 插入全是小写，这样就没有大小写问题了。。。
        name_tokens = api_name.lower().split('.')
        pre_tokenized_tokens = pre_tokenize(
            ' '.join(api_name.split('.'))).lower().split(' ')
        for token in pre_tokenized_tokens:
            if token not in name_tokens and token != '':
                name_tokens.append(token)
        name = ' '.join(name_tokens)

        doc_body = {
            'name': name,
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
                'description': {
                    'query': 'arraylist',
                    'fuzziness': 'auto'
                }
            }
        },
        'from': 0,
        'size': 20
    }
    res = es.search(index=JAVADOC_GLOBAL_NAME, body=query_body)
    print(res)
