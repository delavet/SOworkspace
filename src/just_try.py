import networkx as nx

from util.config import LATEST_CONCEPT_MAP_PATH
from util.concept_map.learn_path_recommender_TYPE0 import recommend_learn_concepts_PACKAGE

def get_all_indexes(sub : str, s : str):
    ret = []
    start_from_index = 0
    while start_from_index < len(s):
        sub_begin_index = s.find(sub,start_from_index)
        sub_end_index = sub_begin_index + len(sub) - 1
        ret.append([sub_begin_index, sub_end_index])
        start_from_index = sub_end_index + 1
    return ret

get_all_indexes('diamond operator' , '''It's called the diamond operator. It was introduced in Java 1.7.''')


if __name__ == "__main__":
    concept_map = nx.read_gexf(LATEST_CONCEPT_MAP_PATH['javadoc'])
    recommend_learn_concepts_PACKAGE(concept_map, 'java.util.concurrent')
    print("\r","1",end="",flush=True)