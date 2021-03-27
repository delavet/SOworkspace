import pickle

import numpy as np

from util.apidoc_semantic.common import preprocess
from util.config import API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH, JAVADOC_GLOBAL_NAME, WORD_EMBEDDING_DIMENTION
from util.constant import *
from util.concept_map.common import get_latest_concept_map
from util.apidoc_search.vector_util import VectorUtil
from util.utils import get_apidoc_wiki_embedding_model

'''
为加速api搜索服务的速度，预先把每个API文档的fasttext向量算好存下来
'''

def pre_generate_short_description_fasttext_vectors(doc_name: str = JAVADOC_GLOBAL_NAME):
    api2vectors = {}
    concept_map = get_latest_concept_map(doc_name)
    vector_util = VectorUtil(get_apidoc_wiki_embedding_model(doc_name))
    # print(vector_util.get_word_similarity('array', 'list'))
    for api in list(concept_map.nodes):
        if NodeAttributes.DESCRIPTION in concept_map.nodes[api].keys():
            processed_desc = preprocess(
                concept_map.nodes[api][NodeAttributes.DESCRIPTION]).lower()
            try:
                desc_vec = vector_util.get_sentence_avg_vector(
                    processed_desc)
                api2vectors[api] = desc_vec
            except:
                print("calculate vector fail for: ", processed_desc)
                api2vectors[api] = np.zeros(WORD_EMBEDDING_DIMENTION)
            
    with open(API_SHORT_DESCRIPTION_FASTTEXT_VECTOR_STORE_PATH[doc_name], 'wb') as wbf:
        pickle.dump(api2vectors, wbf)


if __name__ == "__main__":
    pre_generate_short_description_fasttext_vectors(JAVADOC_GLOBAL_NAME)
