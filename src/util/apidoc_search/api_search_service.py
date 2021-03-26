import networkx as nx
import pickle
import numpy as np

from elasticsearch import Elasticsearch

from util.apidoc_search.vector_util import VectorUtil
from ..config import APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH, JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH
from ..nel.candidate_select import es_wildcard_search, es_search
from ..apidoc_semantic.common import pre_tokenize, preprocess
from ..concept_map.common import get_latest_concept_map


class ApiSearchService:
    def __init__(self, doc_name=JAVADOC_GLOBAL_NAME):
        self.concept_map = get_latest_concept_map(doc_name)
        with open(API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH[doc_name], 'rb') as rbf:
            self.api_short_desc_vectors = pickle.load(rbf)
        self.vector_tool = VectorUtil(APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH[doc_name])
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
        sorted_apis = [item[0] for item in sorted(zipped_apis_sims, key=lambda i : i[1], reverse=True)]
        return sorted_apis
