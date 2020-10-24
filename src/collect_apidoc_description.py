"""
收集apidoc中的描述文本
目前仅针对javadoc
"""
import pickle

from util.config import *
from util.apidoc_semantic.apidoc_description_extractor import collect_concept_description


if __name__ == "__main__":
    javadoc_descriptions = collect_concept_description(JAVADOC_GLOBAL_NAME)
    with open(APIDOC_DESCRIPTION_STORE_PATH[JAVADOC_GLOBAL_NAME], 'wb') as wf:
        pickle.dump(javadoc_descriptions, wf)