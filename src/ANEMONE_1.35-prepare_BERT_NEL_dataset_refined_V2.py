from util.config import ANEMONE_DATASET_STORE_PATH, ANEMONE_BERT_DATASET_FILE_NAME, ANEMONE_BERT_TRAIN_SET_FILE_NAME, ANEMONE_BERT_TEST_SET_FILE_NAME, ANEMONE_GENERAL_DATASET_FILE_NAME, EUREKA_REFINED_LABEL_STORE_PATH, JAVADOC_GLOBAL_NAME
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
import nltk
import os


CASE_THRESHOLD = 5
MAX_LENGTH = 128

concept_map = get_latest_concept_map()
Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
href_attributes = nx.get_node_attributes(concept_map, 'local_href')
description_attributes = nx.get_node_attributes(concept_map, 'description')
api_entities = [
    node for node in concept_map if node in Ntype_attributes and node in href_attributes]
nel_gt_entities = set()
for filename in os.listdir(EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME]):
    if filename.startswith('nel'):
        with open(os.path.join(EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME], filename), 'r', encoding='utf-8') as rf:
            entities = json.load(rf)
            for entity in entities:
                nel_gt_entities.add(entity)

entity_gt_map = {}  # 为了以entity为单位划分数据集（以得到更科学的precision），纪录每个entity的ground_truth, 用thread id_mention name的格式当key来特定是某个thread中的某个mention以防止mention重名


def get_memtion_key_in_entity_gt_map(thread_id, mention):
    return '_'.join([str(thread_id), mention])


def __process_post(context_thread: dict, post_html: str, mention: str, entity: str, label: int) -> list:
    '''
    对一个单独的post处理生成数据项
    post_html: 问题或回答，html字符串
    '''
    global api_entities
    global description_attributes
    global nel_gt_entities
    global entity_gt_map
    global MAX_LENGTH
    ret = None
    if mention not in nel_gt_entities:
        return ret
    try:
        soup = BeautifulSoup(post_html, 'lxml')
        for pre in soup.find_all('pre'):
            pre.extract()
        if mention not in soup.text:
            return None
        sentences = nltk.sent_tokenize(soup.text)
        tags = ', '.join(context_thread['Tags'].strip(
            '<').strip('>').split('><'))
        title = context_thread['Title']
        prefix = tags + '. ' + title + '. '
        sentence_stack = []
        sentence = ''
        # 截取mention出现的一句话以及前面的若干句话加在一起作为sentence，保证整体句子长度不超过MAX_LENGTH
        for s in sentences:
            if mention in s:
                sentence = s  # 2021.3.11 停止使用尽可能增加句子长度的做法，因为这样给模型带来了巨大的数据负担容易爆显存。。
            '''
            if mention in s:
                cur_length = len(nltk.word_tokenize(s))
                sentence = s
                if len(sentence_stack) == 0:
                    break
                temp_s = sentence_stack.pop()
                while len(nltk.word_tokenize(temp_s)) + cur_length < MAX_LENGTH:
                    sentence = temp_s + ' ' + sentence
                    cur_length += len(nltk.word_tokenize(temp_s))
                    if len(sentence_stack) == 0:
                        break
                    else:
                        temp_s = sentence_stack.pop()
                break
            else:
                sentence_stack.append(s)
            '''
        if sentence == '':
            return None
        # sentence = prefix + ' ' + sentence
        entity_desc = get_api_name_from_entity_id(
            entity) + ' description: ' + description_attributes[entity]
        thread_id = context_thread['Id']
        ret = {
            'prefix': prefix,
            'sentence': sentence,
            'mention': mention,
            'entity_desc': entity_desc,
            'entity': entity,
            'label': label,
            'thread_id': str(thread_id)
        }
        if label == 1:
            entity_gt_map[get_memtion_key_in_entity_gt_map(
                thread_id, mention)] = entity
        '''
        for sentence in sentences:
            if mention in sentence:
                ret.append({
                    'sentence': sentence,
                    'mention': mention,
                    'entity_desc': get_api_name_from_entity_id(entity) + ' description: ' + description_attributes[entity],
                    'label': label
                })
        '''
    except Exception as e:
        # print(e)
        return None
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
        posts.append(answer['Body'])
    for post in posts:
        data = __process_post(context,
                              post, case['mention'], case['entity'], case['label'])
        if data is not None:
            ret.append(data)
    return ret


def __select_cases(cases: list, threshold: int) -> list:
    '''
    对同一个mention，控制加入数据集的label为0的个数
    在general的数据集中1一个label为1的有8个反例，感觉有点过多了不太能收敛
    可以用这个函数调整label为0和1的数据的比例
    '''
    ret = [case for case in cases if case['label'] == 1]
    rest = [case for case in cases if case['label'] == 0]
    if threshold >= len(cases):
        return cases
    for i in range(threshold - 1):
        ret.append(rest[i])
    return ret


def generate_bert_dataset_from_general_dataset(general_dataset_file_path, target_doc=JAVADOC_GLOBAL_NAME):
    global CASE_THRESHOLD
    global entity_gt_map
    bert_dataset = []
    with open(general_dataset_file_path, "r", encoding="utf-8") as rf, open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_DATASET_FILE_NAME), 'w', encoding="utf-8") as wf, open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], 'entity_gt_map.json'), 'w', encoding="utf-8") as wf_gt:
        general_dataset = json.load(rf)
        cur_mention = ''
        temp_cases = []
        for case in tqdm(general_dataset):
            if case['mention'] == cur_mention:
                temp_cases.append(case)
            else:
                selected_cases = __select_cases(temp_cases, CASE_THRESHOLD)
                for c in selected_cases:
                    bert_dataset.extend(
                        process_general_case(c)
                    )
                temp_cases = [case]
                cur_mention = case['mention']

        print(len(bert_dataset))
        wf.writelines([json.dumps(data, ensure_ascii=False) +
                       '\n' for data in bert_dataset])
        json.dump(entity_gt_map, wf_gt, ensure_ascii=False, indent=2)
        print(len(list(entity_gt_map.keys())))
        # json.dump(bert_dataset, wf, ensure_ascii=False, indent=2)
    with open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_TRAIN_SET_FILE_NAME), 'w', encoding="utf-8") as wf_train, open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_TEST_SET_FILE_NAME), 'w', encoding="utf-8") as wf_test:
        mentions = list(entity_gt_map.keys())
        random.shuffle(mentions)
        split_index = len(mentions) - len(mentions) // 10
        train_mentions = set(mentions[:split_index])
        test_mentions = set(mentions[split_index:])
        train_set = [
            case for case in bert_dataset if get_memtion_key_in_entity_gt_map(case['thread_id'], case['mention']) in train_mentions]
        test_set = [
            case for case in bert_dataset if get_memtion_key_in_entity_gt_map(case['thread_id'], case['mention']) in test_mentions]
        # random.shuffle(bert_dataset)
        # split_index = len(bert_dataset) - len(bert_dataset) // 10
        # train_set = bert_dataset[:split_index]
        # test_set = bert_dataset[split_index:]
        wf_train.writelines([json.dumps(data, ensure_ascii=False) +
                             '\n' for data in train_set])
        wf_test.writelines([json.dumps(data, ensure_ascii=False) +
                            '\n' for data in test_set])
        #json.dump(train_set, wf_train, indent=2, ensure_ascii=False)
        #json.dump(test_set, wf_test, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_bert_dataset_from_general_dataset(os.path.join(
        ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_GENERAL_DATASET_FILE_NAME))
