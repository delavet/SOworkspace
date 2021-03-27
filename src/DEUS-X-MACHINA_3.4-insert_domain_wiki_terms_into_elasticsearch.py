import networkx as nx
import wikipedia

from elasticsearch import Elasticsearch
from tqdm import tqdm
from util.apidoc_semantic.common import pre_tokenize, preprocess
from util.config import JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, FUDAN_CONCEPT_MAP_PATH, Elasticsearch_term_index_name_template
from util.constant import *
from util.concept_map.common import get_latest_hyper_concept_map
from util.utils import single_line_print

'''
向es中插入domain term和wiki term，
方便基于概念的API搜索
'''

es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)
fudan_concept_map = nx.read_gpickle(FUDAN_CONCEPT_MAP_PATH[JAVADOC_GLOBAL_NAME])


def gather_term_description(node_id, term_type, doc_name = JAVADOC_GLOBAL_NAME):
    '''
    收集term的文本，插入elasticsearch用于进一步的embedding训练，也方便搜索
    由于用到了复旦的图谱，这个方法还不是全文档通用】
    ### 句子没有被预处理！
    '''
    if term_type == NodeType.DOMAIN_TERM:
        pred_sentences = [node for node in list(fudan_concept_map.pred[node_id]) if 'sentence' in fudan_concept_map.nodes[node]['labels']]
        sentences = [fudan_concept_map.nodes[node]['properties'].get('sentence_name', '') for node in pred_sentences]
        return '\n'.join(sentences)
    else:
        properties = fudan_concept_map.nodes[node_id]['properties']
        name = properties.get('wikidata_name', None)
        if name is None:
            name = properties.get('name', None)
        if name is None:
            name = properties.get('labels_en', None)
        if name is None:
            return ''
        try:
            page = wikipedia.page(name)
        except:
            single_line_print(f'failed to find page: {name}')
            return ''
        return page


def insert_domain_wiki_terms_into_elasticsearch(doc_name: str = JAVADOC_GLOBAL_NAME):
    global es
    hyper_concept_map = get_latest_hyper_concept_map(doc_name)
    index = -1
    term_nodes = [node for node in hyper_concept_map.nodes if hyper_concept_map.nodes[node].get(
        NodeAttributes.Ntype, '') == NodeType.DOMAIN_TERM or hyper_concept_map.nodes[node].get(NodeAttributes.Ntype, '') == NodeType.WIKI_TERM]
    for node in tqdm(term_nodes):
        term_name = hyper_concept_map.nodes[node].get(NodeAttributes.NAME, '')
        term_type = hyper_concept_map.nodes[node][NodeAttributes.Ntype]
        processed_term_name = preprocess(pre_tokenize(term_name)).lower()
        description = gather_term_description(
            node, hyper_concept_map.nodes[node][NodeAttributes.Ntype], doc_name)
        doc_body = {
            'name': processed_term_name, # 处理后的term名，小写的
            'term_name': term_name, #原先的term名
            'term_id': node, # term在concept map中的id
            'term_type': term_type, # term类型：两种
            'description': description #描述文本
        }
        index += 1
        index_name = Elasticsearch_term_index_name_template.format(doc_name)
        es.index(index = index_name, doc_type='term', id = index, body=doc_body)


if __name__ == "__main__":
    insert_domain_wiki_terms_into_elasticsearch(JAVADOC_GLOBAL_NAME)
    print('insert over, have a try for search')
    # 插入完了试一下查询
    query_body = {
        'query': {
            'match': {
                'name': {
                    'query': 'list',
                    'fuzziness': 'auto'
                }
            }
        },
        'from': 0,
        'size': 20
    }
    res = es.search(index=Elasticsearch_term_index_name_template.format(
        JAVADOC_GLOBAL_NAME), body=query_body)
    print(res)
