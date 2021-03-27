import pickle
import numpy as np
from tqdm.std import tqdm
from util.apidoc_semantic.common import pre_tokenize, preprocess
from util.concept_map.common import get_latest_hyper_concept_map

from util.config import DOMAIN_WIKI_TERM_FASTTEXT_VECTOR_STORE_PATH, JAVADOC_GLOBAL_NAME,Elasticsearch_host, Elasticsearch_port, Elasticsearch_term_index_name_template, WORD_EMBEDDING_DIMENTION
from util.constant import *
from elasticsearch import Elasticsearch
from util.utils import get_apidoc_wiki_embedding_model
from util.apidoc_search.vector_util import VectorUtil

'''
为加速term搜索服务的速度，预先把每个term文档的fasttext向量算好存下来
'''

def pre_generate_term_fasttext_vectors(doc_name: str = JAVADOC_GLOBAL_NAME):
    term_id2vector = {}
    vector_util = VectorUtil(get_apidoc_wiki_embedding_model(doc_name))
    es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)
    hyper_concept_map = get_latest_hyper_concept_map(doc_name)
    term_nodes = [node for node in hyper_concept_map.nodes if hyper_concept_map.nodes[node].get(
        NodeAttributes.Ntype, '') == NodeType.DOMAIN_TERM or hyper_concept_map.nodes[node].get(NodeAttributes.Ntype, '') == NodeType.WIKI_TERM]
    for node in tqdm(term_nodes):
        vec = [0] * WORD_EMBEDDING_DIMENTION
        query_body = {
            'query': {
                'match': {
                    'term_id': {
                        'query': node
                    }
                }
            }
        }
        es_res = es.search(index=Elasticsearch_term_index_name_template.format(doc_name), filter_path='hits.hits._source.description',
                           body=query_body)
        if len(es_res.keys()) == 0:
            term_id2vector[node] = vec
            continue
        ret = [item['_source']['description'] for item in es_res['hits']['hits']]
        if len(ret) == 0:
            term_id2vector[node] = vec
            continue
        sentence = ret[0]
        processed_sentence = preprocess(pre_tokenize(sentence))
        processed_sentence = ' '.join(processed_sentence.split()).lower()
        try:
            vec = vector_util.get_sentence_avg_vector(processed_sentence)
        except:
            vec = [0] * WORD_EMBEDDING_DIMENTION
        term_id2vector[node] = vec
    with open(DOMAIN_WIKI_TERM_FASTTEXT_VECTOR_STORE_PATH[doc_name], 'wb') as wbf:
        pickle.dump(term_id2vector, wbf)

if __name__ == "__main__":
    pre_generate_term_fasttext_vectors(JAVADOC_GLOBAL_NAME)
