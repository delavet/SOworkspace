import json

from util.concept_map.common import get_latest_concept_map
from util.config import MENIA_WHOLE_PREDICTION_STORE_PATH, MENIA_CLASS_LEVEL_PREDICTION_STORE_PATH, JAVADOC_GLOBAL_NAME
from util.constant import *


'''
将预测中提到的所有method和filed都变为对应的class
这样可以将API变得更加集中，可能更有利于社群检测
是执行MENIA之前准备工作的可选项，实验的时候可以试试
'''

concept_map = get_latest_concept_map()


def turn_to_class_level_api(api: str):
    global concept_map
    Ntype = concept_map.nodes[api].get(NodeAttributes.Ntype, '')
    if Ntype not in field_level_node_types:
        return api
    else:
        preds = list(concept_map.pred[api])
        for pred in preds:
            if concept_map[pred][api][EdgeAttrbutes.Etype] == EdgeType.INCLUDE and concept_map.nodes[pred].get(NodeAttributes.Ntype, '') in class_level_node_types:
                return pred
    return api


def transfer_MENIA_predictions(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(MENIA_WHOLE_PREDICTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        all_predictions = dict(json.load(rf))
    class_predictions = {}
    for thread_id, mentions in all_predictions.items():
        new_mentions = {}
        for mention, api in mentions.items():
            new_api = turn_to_class_level_api(api)
            new_mentions[mention] = new_api
        class_predictions[thread_id] = new_mentions
    with open(MENIA_CLASS_LEVEL_PREDICTION_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(class_predictions, wf, indent=2, ensure_ascii=False)
    

if __name__ == "__main__":
    transfer_MENIA_predictions(JAVADOC_GLOBAL_NAME)