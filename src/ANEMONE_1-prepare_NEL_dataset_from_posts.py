from networkx.classes import graphviews
from util.config import SO_POSTS_STORE_PATH, ANEMONE_DATASET_STORE_PATH, JAVADOC_GLOBAL_NAME, ANEMONE_GENERAL_DATASET_FILE_NAME, APIDOC_API_URL_REGEX_PATTERN, TEMP_FILE_STORE_PATH, EUREKA_REFINED_LABEL_STORE_PATH
from util.constant import SO_POST_STOP_WORDS
from util.concept_map.common import get_latest_concept_map, get_relative_path_from_href
from util.nel.candidate_select import get_gt_candidate, simple_candidate_selector, substring_candidate_selector, es_candidate_selector
from bs4 import BeautifulSoup
from util.utils import get_all_indexes
from tqdm import tqdm

import os
import pickle
import json
import re
import networkx as nx


'''
ANEMONE-1
ANEMONE的任务是根据EUREKA识别出的API实体mention，去特定与文档中API实体的链接
ANEMONE-1首先为NEL任务准备一个general的数据集，包含为一个实体链接所需的各种general信息，之后再根据具体方法对general的数据集做精化
大概步骤：
1. 遍历post，找到其中和API关联的mention（检测<a>标签，识别路径）
2. 为mention找到候选实体（暂定4个），其中一个正例（API文档路径精确匹配），三个反例（mention与API name的公共序列达到3以上）
3. 每个候选实体构建一个case，包含信息：
    （1）mention与对应concept map中的候选实体ID（即候选实体的context）
    （2）mention的context（整个thread的数据）
    （3）是否匹配的label
'''


nel_gt_entities = set()  # 经过refine标注后确定是在描述api的mention
for filename in os.listdir(EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME]):
    if filename.startswith('nel'):
        with open(os.path.join(EUREKA_REFINED_LABEL_STORE_PATH[JAVADOC_GLOBAL_NAME], filename), 'r', encoding='utf-8') as rf:
            entities = json.load(rf)
            for entity in entities:
                nel_gt_entities.add(entity)


def _generate_nel_data(post_body: str, context_thread: dict, target_doc: str = JAVADOC_GLOBAL_NAME) -> list:
    '''
    对一个具体的post（question或answer）做NEL数据的抽取，大概过程就是上面综述所说
    ## parameter
    `post_body` : 可能是问题也可能是回答
    `context_thread` : 作为上下文的整个thread，可能用在之后的 抽取步骤
    `target_doc` : 目标APIDOC类型
    ## return
    返回该post中能够分析出的NEL数据列表
    '''
    global nel_gt_entities
    ret = []
    try:
        soup = BeautifulSoup(post_body, 'lxml')
        for pre in soup.find_all('pre'):
            pre.extract()
        # 筛选包含API超链接的mention
        # 指向api的才要、太短的句子不要。。。
        a_s = [a for a in soup.find_all('a') if len(a.text) > 3 and re.search(
            APIDOC_API_URL_REGEX_PATTERN[JAVADOC_GLOBAL_NAME], a.get('href')) is not None and a.text.lower() not in SO_POST_STOP_WORDS]
        if len(a_s) <= 0:
            return ret
        # 为每个超链接构建NEL数据集case
        for a in a_s:
            mention = a.text
            if mention not in nel_gt_entities:
                continue  # 2021.3.5 如果不在标注过的实体mention中就跳过，有点激进不知道数据量会不会太小，如果不行再改回去
            ground_truth_url = a.get('href')
            ground_truth_entity = get_gt_candidate(mention, ground_truth_url)
            # 没找到ground truth则不构建他的数据了
            if ground_truth_entity is None:
                continue
            temp_counter = 0
            candidates = set([ground_truth_entity])
            # 2021.3.5 改进为基于elasticsearch的candidate选择器
            for candidate in es_candidate_selector(mention):
                candidates.add(candidate)
                temp_counter += 1
                if temp_counter > 8:  # 最多给8个反例吧，给一个反例目前来看训练出来没啥用处
                    break
            for candidate_entity in candidates:
                ret.append(
                    {
                        'mention': mention,
                        'entity': candidate_entity,
                        'label': 1 if candidate_entity == ground_truth_entity else 0,
                        'context': context_thread
                    }
                )
    except Exception as e:
        print(e)
        return ret
    return ret


def transfer_posts2general_dataset(post_file_path: str, target_doc: str = JAVADOC_GLOBAL_NAME) -> list:
    '''
    针对某个具体的post存储文件，处理其中的所有post，生成general的数据集
    ## parameter
    `post_file_path` : post的文件名，文件应该为pkl格式
    ## return
    返回`list`，内部每个都是NEL的数据集格式，例如：
    ```json

    ```
    '''
    if not post_file_path.endswith('.pkl'):
        return []
    ret = []
    with open(post_file_path, 'rb') as rbf:
        print(f'processing {post_file_path}')
        threads = pickle.load(rbf)
        for i, thread in tqdm(enumerate(threads)):
            question = thread['Body']
            answers = [item['Body'] for item in thread['Answers']]
            ret.extend(_generate_nel_data(question, thread, target_doc))
            for answer in answers:
                ret.extend(_generate_nel_data(answer, thread, target_doc))
            # print("\r", f"{i} of {len(threads)} threads processed", end="", flush=True)
    print(f'{post_file_path} processed')
    return ret


def generate_nel_general_dataset_for_javadoc():
    '''
    给javadoc生成对应的NEL数据集
    '''
    javadoc_so_post_filenames = os.listdir(SO_POSTS_STORE_PATH['<java>'])
    with open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_GENERAL_DATASET_FILE_NAME), 'w', encoding='utf-8') as wf:
        dataset = []
        for filename in javadoc_so_post_filenames:
            partial_general_dataset = transfer_posts2general_dataset(
                os.path.join(SO_POSTS_STORE_PATH['<java>'], filename), JAVADOC_GLOBAL_NAME)
            dataset.extend(partial_general_dataset)
            with open(os.path.join(TEMP_FILE_STORE_PATH, f'general_nel_dataset_from_post_0_to_{filename}.json'), 'w', encoding='utf-8') as wf_temp:
                json.dump(dataset, wf_temp, ensure_ascii=False, indent=2)
        json.dump(dataset, wf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    switch = {
        JAVADOC_GLOBAL_NAME: generate_nel_general_dataset_for_javadoc
    }
    # 后续可以改成别的文档
    switch[JAVADOC_GLOBAL_NAME]()
