from util.config import SO_POSTS_STORE_PATH, EUREKA_DATASET_STORE_PATH, EUREKA_FULL_DATASET_FILE_NAME, JAVADOC_GLOBAL_NAME, APIDOC_ROOT_URL, APIDOC_API_URL_REGEX_PATTERN
from bs4 import BeautifulSoup
from util.utils import get_all_indexes
from tqdm import tqdm

import os
import pickle
import json
import re

'''
EUREKA-2
EUREKA的任务是：从post中识别所有可能与文档相连的API实体
这被抽象为一个NER任务，其中训练数据使用从post中收集的天然ground-truth
EUREKA为NER任务准备训练数据集
'''


def _generate_train_data(sentence : str, target_doc : str = JAVADOC_GLOBAL_NAME):
    '''
    将post中的一段话进行分析给出对应的NER训练数据
    ## parameter
    `sentence` : 可能是问题也可能是回答
    `target_doc` : 目标APIDOC类型，是以SO中的tag形式给出的，如javadoc就是匹配<java>
    ## return
    返回该句话中能够分析出的训练数据列表
    '''
    ret = []
    #随处可见的超链接会用的词，对训练可能只有坏处...
    stop_words = ['here', 'this', 'javadoc', 'javadocs', 'docs', 'documentation', 'the documentation', 'doc', 'the javadoc', 'java docs', 'java doc', 'java documentation', 'the docs ']
    try:
        soup = BeautifulSoup(sentence, 'lxml')
        for pre in soup.find_all('pre'):
            pre.extract()
        #筛选包含目标文档链接的超链接
        #指向api的才要、太短的句子不要。。。
        a_texts = [a.text for a in soup.find_all('a') if len(a.text) > 1 and re.search(APIDOC_API_URL_REGEX_PATTERN[JAVADOC_GLOBAL_NAME], a.get('href')) is not None and a.text.lower() not in stop_words]
        if len(a_texts) <= 0:
            return ret
        #原来这里直接按行切分，现在按照句号问号冒号叹号分割，试图让分割出来的句子短一些
        #lines = soup.text.split('\n')
        lines = re.split(r'(\s*(\.|:|\?|!|\~)\s+|\n)+', soup.text)
        candidate_lines = [line for line in lines if any([t for t in a_texts if t in line]) and len(line.split(' ')) > 2]
        for candidate in candidate_lines:
            train_data = {
                "text" : candidate,
                "label" : {
                    "api" : {}
                }
            }
            labels = {}
            for a_text in a_texts:
                if a_text in candidate:
                    labels[a_text] = get_all_indexes(a_text, candidate)
            train_data["label"]["api"] = labels
            ret.append(train_data)
    except:
        return ret
    return ret


def transfer_posts2trainset(post_file_path : str, target_doc : str = JAVADOC_GLOBAL_NAME):
    '''
    针对某个具体的post存储文件，处理其中的所有post，生成对应训练数据
    ## parameter
    `post_file_path` : post的文件名，文件应该为pkl格式
    ## return
    返回`list`，内部每个都是NER的训练数据格式，例如：
    ```json
    [{'text': "It's called the diamond operator. It was introduced in Java 1.7.",'label': {'api': {'diamond operator': [[16, 31]]}}}]
    ```
    '''
    if not post_file_path.endswith('.pkl'):
        return []
    ret = []
    with open(post_file_path, 'rb') as rbf:
        posts = pickle.load(rbf)
        for post in posts:
            question = post['Body']
            answers = [item['Body'] for item in post['Answers']]
            ret.extend(_generate_train_data(question, target_doc))
            for answer in answers:
                ret.extend(_generate_train_data(answer, target_doc))
    return ret


def generate_ner_dataset_for_javadoc():
    '''
    专门生成javadoc对应的NER数据集
    '''
    javadoc_so_post_filenames = os.listdir(SO_POSTS_STORE_PATH['<java>'])
    with open(os.path.join(EUREKA_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], EUREKA_FULL_DATASET_FILE_NAME), 'w', encoding='utf-8') as wf:
        for filename in tqdm(javadoc_so_post_filenames):
            partial_dataset = transfer_posts2trainset(
                os.path.join(SO_POSTS_STORE_PATH['<java>'], filename),
                JAVADOC_GLOBAL_NAME
            )
            wf.writelines([json.dumps(d) + '\n' for d in partial_dataset])


if __name__ == "__main__":
    #后续可以加个分支处理别的文档
    generate_ner_dataset_for_javadoc()
