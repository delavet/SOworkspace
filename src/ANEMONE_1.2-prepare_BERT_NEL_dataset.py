import os
from util.config import ANEMONE_DATASET_STORE_PATH, ANEMONE_BERT_DATASET_FILE_NAME, ANEMONE_BERT_TRAIN_SET_FILE_NAME, ANEMONE_BERT_TEST_SET_FILE_NAME, ANEMONE_GENERAL_DATASET_FILE_NAME, APIDOC_DESCRIPTION_STORE_PATH, JAVADOC_GLOBAL_NAME
from util.concept_map.common import get_latest_concept_map
from util.nel.common import get_api_name_from_entity_id
from util.utils import get_html_text_except_code
from bs4 import BeautifulSoup
from tqdm import tqdm

import networkx as nx
import pickle
import re
import json
import random


concept_map = get_latest_concept_map()
Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
href_attributes = nx.get_node_attributes(concept_map, 'local_href')
description_attributes = nx.get_node_attributes(concept_map, 'description')
api_entities = [
    node for node in concept_map if node in Ntype_attributes and node in href_attributes]


def __process_post(post_html: str, mention: str, entity: str, label: int) -> list:
    '''
    对一个单独的post处理生成数据项
    post_html: 问题或回答，html字符串
    '''
    global api_entities
    global description_attributes
    ret = []
    try:
        soup = BeautifulSoup(post_html, 'lxml')
        for pre in soup.find_all('pre'):
            pre.extract()
        sentences = re.split(r'(\s*(\.|:|\?|!|\~)\s+|\n)+', soup.text)
        for sentence in sentences:
            if mention in sentence:
                ret.append({
                    'sentence': sentence,
                    'mention': mention,
                    'entity_desc': get_api_name_from_entity_id(entity) + ' description: ' + description_attributes[entity],
                    'label': label
                })
    except:
        return ret
    return ret


def process_general_case(case: dict):
    '''
    处理一个general的case变成BERT的训练集格式
    general的case长啥样见ANEMONE 1.1，1.2就不展示了
    '''
    ret = []
    context = case['context']
    posts = []
    posts.append(context['Body'])
    for answer in context['Answers']:
        posts.append(context['Body'])
    for post in posts:
        ret.extend(__process_post(
            post, case['mention'], case['entity'], case['label']))
    return ret


def generate_bert_dataset_from_general_dataset(general_dataset_file_path, target_doc=JAVADOC_GLOBAL_NAME):
    bert_dataset = []
    with open(general_dataset_file_path, "r", encoding="utf-8") as rf, open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_DATASET_FILE_NAME), 'w', encoding="utf-8") as wf:
        general_dataset = json.load(rf)
        for case in tqdm(general_dataset):
            bert_dataset.extend(
                process_general_case(case)
            )
        print(len(bert_dataset))
        wf.writelines([json.dumps(data, ensure_ascii=False) +
                       '\n' for data in bert_dataset])
        # json.dump(bert_dataset, wf, ensure_ascii=False, indent=2)
    with open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_TRAIN_SET_FILE_NAME), 'w', encoding="utf-8") as wf_train, open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_TEST_SET_FILE_NAME), 'w', encoding="utf-8") as wf_test:
        random.shuffle(bert_dataset)
        split_index = len(bert_dataset) - 5000
        train_set = bert_dataset[:split_index]
        test_set = bert_dataset[split_index:]
        wf_train.writelines([json.dumps(data, ensure_ascii=False) +
                             '\n' for data in train_set])
        wf_test.writelines([json.dumps(data, ensure_ascii=False) +
                            '\n' for data in test_set])
        #json.dump(train_set, wf_train, indent=2, ensure_ascii=False)
        #json.dump(test_set, wf_test, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_bert_dataset_from_general_dataset(os.path.join(
        ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_GENERAL_DATASET_FILE_NAME))
