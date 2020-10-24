from util.concept_map import apidoc_concept_map_generator
import networkx as nx
from util.config import *
import os


'''
generate concept map for javadoc
'''
def generate_concept_map_for_javadoc():
    concept_map = apidoc_concept_map_generator.generate_concept_map('javadoc')
    print('generate complete!')
    nx.write_gexf(concept_map, LATEST_CONCEPT_MAP_PATH['javadoc'])


if __name__ == "__main__":
    generate_concept_map_for_javadoc()
