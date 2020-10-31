import networkx as nx

from util.config import LATEST_CONCEPT_MAP_PATH
from util.concept_map.learn_path_recommender_TYPE0 import recommend_learn_concepts_PACKAGE


if __name__ == "__main__":
    concept_map = nx.read_gexf(LATEST_CONCEPT_MAP_PATH['javadoc'])
    recommend_learn_concepts_PACKAGE(concept_map, 'java.util.concurrent')
    print("\r","1",end="",flush=True)