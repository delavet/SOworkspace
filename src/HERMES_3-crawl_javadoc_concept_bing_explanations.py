from bing_concept_description_crawler.bing_crawler import crawl_concept, prepare_for_crawl
from util.config import APIDOC_DESCRIPTION_STORE_PATH, BING_API_CONCEPT_STORE_PATH, JAVADOC_GLOBAL_NAME

import pickle
import time
import random


def crawl_javadoc_concept_bing_explanations():
    #crawl 3000 sample of concept bing descriptions for an early validation, will be processed during the full validation
    with open(APIDOC_DESCRIPTION_STORE_PATH[JAVADOC_GLOBAL_NAME], 'rb') as rbf, open(BING_API_CONCEPT_STORE_PATH[JAVADOC_GLOBAL_NAME]['large'], 'wb') as wbf:
        concept_descriptions = pickle.load(rbf)
        concept_names = list(concept_descriptions.keys())
        random_evaluate_concepts = random.sample(concept_names, 3000)
        concept_web_descs = []
        prepare_for_crawl()
        for name in random_evaluate_concepts:
            concept_web_descs.append(
                crawl_concept(name)
            )
            time.sleep(5+random.randint(-2, 3))
        pickle.dump(concept_web_descs, wbf)


def crawl_javadoc_concept_bing_explanations_sample():
    #only crawl 300 sample of concept bing descriptions for an early validation
    # a full version crawl will be executed when the real validation is going to be processed 
    with open(APIDOC_DESCRIPTION_STORE_PATH[JAVADOC_GLOBAL_NAME], 'rb') as rbf, open(BING_API_CONCEPT_STORE_PATH[JAVADOC_GLOBAL_NAME]['sample'], 'wb') as wbf:
        concept_descriptions = pickle.load(rbf)
        concept_names = list(concept_descriptions.keys())
        random_evaluate_concepts = random.sample(concept_names, 300)
        concept_web_descs = []
        prepare_for_crawl()
        for name in random_evaluate_concepts:
            concept_web_descs.append(
                crawl_concept(name)
            )
            time.sleep(5+random.randint(-2, 3))
        pickle.dump(concept_web_descs, wbf)
        


if __name__ == "__main__":
    crawl_javadoc_concept_bing_explanations_sample()