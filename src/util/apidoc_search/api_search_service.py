import math
import networkx as nx
import pickle
from nltk.jsontags import register_tag
import numpy as np

from elasticsearch import Elasticsearch

from ..constant import *
from util.apidoc_search.vector_util import VectorUtil
from ..config import APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH, DOMAIN_WIKI_TERM_FASTTEXT_VECTOR_STORE_PATH, Elasticsearch_term_index_name_template, JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH
from ..nel.candidate_select import es_wildcard_search, es_search
from ..apidoc_semantic.common import extract_noun_chunks, pre_tokenize, preprocess
from ..concept_map.common import get_latest_hyper_concept_map
from ..utils import get_apidoc_wiki_embedding_model, get_node2vec_model


class ApiSearchService:
    def __init__(self, doc_name=JAVADOC_GLOBAL_NAME):
        self.hyper_concept_map = get_latest_hyper_concept_map(doc_name)
        with open(API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH[doc_name], 'rb') as rbf:
            self.api_short_desc_vectors = pickle.load(rbf)
        with open(DOMAIN_WIKI_TERM_FASTTEXT_VECTOR_STORE_PATH[doc_name], 'rb') as rbf2:
            self.term_vectors = pickle.load(rbf2)
        self.node2vec_model = get_node2vec_model(doc_name)
        self.vector_tool = VectorUtil(get_apidoc_wiki_embedding_model(doc_name))
        self.es = Elasticsearch(hosts=Elasticsearch_host,
                                port=Elasticsearch_port)

    def search_literally(self, query: str):
        processed_query = preprocess(query).lower()
        result_apis = set()
        name_search_result = es_search(query, 'name')
        result_apis.update(name_search_result)
        desc_search_result = es_search(query, 'description')
        result_apis.update(desc_search_result)
        if len(result_apis) == 0:
            name_search_result = es_search(query, 'name', 'auto')
            result_apis.update(name_search_result)
            desc_search_result = es_search(
                query, 'description', 'auto')
            result_apis.update(desc_search_result)
        if len(result_apis) == 0:
            name_search_result = es_wildcard_search(query, 'name')
            result_apis.update(name_search_result)
            desc_search_result = es_wildcard_search(
                query, 'description')
            result_apis.update(desc_search_result)
        result_apis = list(result_apis)
        api_desc_vectors = [np.array(
            self.api_short_desc_vectors.get(api, np.zeros(100))) for api in result_apis]
        query_vec = np.array(
            self.vector_tool.get_sentence_avg_vector(processed_query))
        sims = VectorUtil.cosine_similarities(query_vec, api_desc_vectors).tolist()
        zipped_apis_sims = zip(result_apis, sims)
        sorted_apis = [item for item in sorted(zipped_apis_sims, key=lambda i : i[1], reverse=True)]
        return sorted_apis

    def search_term(self, query: str):
        query_body = {
            'query': {
                'match': {
                    'name': {
                        'query': query,
                        'fuzziness': 'auto'
                    }
                }
            }
        }
        res = self.es.search(index=Elasticsearch_term_index_name_template.format(
            JAVADOC_GLOBAL_NAME), filter_path='hits.hits._source.term_id', body=query_body)
        if len(res.keys()) == 0:
            return []
        ret = [int(item['_source']['term_id']) for item in res['hits']['hits']]
        return ret

    def search_by_concept(self, query: str):
        processed_query = preprocess(query).lower()
        query_word_embedding = self.vector_tool.get_sentence_avg_vector(processed_query)
        query_noun_chunks = extract_noun_chunks(query)
        candidate_apis = set()
        query_node2vec_embedding_list = []
        query_node2vec_embedding_weight_list = []
        
        for noun_chunk in query_noun_chunks:
            related_terms = self.search_term(noun_chunk)
            related_term_word2vecs = {}
            for term_id in related_terms:
                if not np.any(self.term_vectors.get(term_id, [0])):
                    continue
                related_term_word2vecs[term_id] = self.term_vectors.get(term_id)
            if len(related_term_word2vecs) == 0:
                continue
            for term_id in related_terms:
                #获取候选API结点
                bfs_tree = nx.bfs_tree(
                    self.hyper_concept_map, term_id, reverse=True, depth_limit=2)
                candidate_apis.update([node for node in bfs_tree.nodes if self.hyper_concept_map.nodes[node].get(NodeAttributes.Ntype) not in term_level_node_types])

                # 计算query的node2vec
                term_node2vec_embedding = self.node2vec_model.wv[str(term_id)]
                term_word2vec_embedding = related_term_word2vecs.get(term_id)
                if not np.any(term_word2vec_embedding):
                    continue
                term_weight = VectorUtil.similarity(term_word2vec_embedding, query_word_embedding) / float(
                    len(query_noun_chunks) * len(related_term_word2vecs))
                query_node2vec_embedding_list.append(term_node2vec_embedding)
                query_node2vec_embedding_weight_list.append(term_weight)
        query_node_embedding = VectorUtil.get_weight_mean_vec(query_node2vec_embedding_list, query_node2vec_embedding_weight_list)
        candidate_apis = list(candidate_apis)
        api_desc_vectors = [np.array(
            self.api_short_desc_vectors.get(api, np.zeros(100))) for api in candidate_apis]
        api_node_vectors = [np.array(self.node2vec_model.wv[api]) for api in candidate_apis]
        query_word_embedding = np.array(query_word_embedding)
        query_node_embedding = np.array(query_node_embedding)
        word_sims = VectorUtil.cosine_similarities(
            query_word_embedding, api_desc_vectors).tolist()
        node_sims = VectorUtil.cosine_similarities(
            query_node_embedding, api_node_vectors).tolist()
        sims = [0.7 * word_sim + 0.3 * node_sim for word_sim, node_sim in zip(word_sims, node_sims)]
        zipped_apis_sims = zip(candidate_apis, sims)
        sorted_apis = [item for item in sorted(
            zipped_apis_sims, key=lambda i: i[1], reverse=True)]
        begin_add = False
        ret = []
        for item in sorted_apis:
            if begin_add:
                ret.append(item)
            else:
                if not math.isnan(item[1]):
                    begin_add = True
                    ret.append(item)
        return ret[:50]
