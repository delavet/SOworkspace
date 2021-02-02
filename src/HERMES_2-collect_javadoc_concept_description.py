"""
收集apidoc中的描述文本
目前仅针对javadoc
"""
import pickle
import json

from util.config import *
from util.apidoc_semantic.apidoc_description_extractor import collect_concept_description


if __name__ == "__main__":
    javadoc_descriptions = collect_concept_description(JAVADOC_GLOBAL_NAME)
    with open(APIDOC_DESCRIPTION_STORE_PATH[JAVADOC_GLOBAL_NAME], 'w', encoding="utf-8") as wf:
        json.dump(javadoc_descriptions, wf, ensure_ascii=False, indent=2)
