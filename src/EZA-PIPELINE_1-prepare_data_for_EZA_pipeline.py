'''
EUREKA、ZAMPATHA、ANEMONE三个部分组合成整体的pipeline完成SO帖子与API的链接
这个pipeline主要在torch的env下实现，因此主体代码不在SOworkspace里（最后会拷贝回来）
本文件为pipeline准备输入的数据
'''
from util.config import SO_POSTS_STORE_PATH, EUREKA_DATASET_STORE_PATH, EUREKA_FULL_DATASET_FILE_NAME, JAVADOC_GLOBAL_NAME, EZA_PIPELINE_DATA_STORE_PATH, EZA_PIPELINE_INPUT_FILE_NAME
from bs4 import BeautifulSoup
from util.utils import get_all_indexes
from tqdm import tqdm
import nltk

import os
import pickle
import json
import re


def _generate_data_from_sentence(sentence: str, thread_id, target_doc: str = JAVADOC_GLOBAL_NAME):
    '''
    将post中的一段话进行分析给出对应的NER训练数据
    ## parameter

    `sentence` : 可能是问题也可能是回答
    `thread_id` : 对应thread的id，因为有可能
    `target_doc` : 目标APIDOC类型
    ## return
    返回该句话中能够分析出的训练数据列表
    '''
    ret = []
    try:
        soup = BeautifulSoup(sentence, 'lxml')
        for pre in soup.find_all('pre'):
            pre.extract()

        #lines = soup.text.split('\n')
        # lines = nltk.sent_tokenize(soup.text)
        lines = re.split(r'(\s*(\.|:|\?|!|\~)\s+|\n)+', soup.text)
        candidate_lines = [line for line in lines if len(
            nltk.word_tokenize(line)) > 3]
        for candidate in candidate_lines:
            data = {
                "thread_id": thread_id,
                "text": candidate,
                "label": {
                    "api": {}
                }
            }
            ret.append(data)
    except:
        return ret
    return ret


def transfer_posts2EZAdata(post_file_path: str, index: int, target_doc: str = JAVADOC_GLOBAL_NAME):
    '''
    针对某个具体的post存储文件，处理其中的所有post，生成交给EZA pipeline处理的数据
    ## parameter

    `post_file_path` : post的文件名，文件应该为pkl格式
    ## return

    返回`list`，内部每个都是初始交给EZA pipeline的格式，例如：
    ```json
    [{'text': "It's called the diamond operator. It was introduced in Java 1.7.",'label': {'api': {}}]
    ```
    这里的label什么都没有，因为是等待EUREKA给出预测
    '''
    if not post_file_path.endswith('.pkl'):
        return []
    ret = []
    with open(post_file_path, 'rb') as rbf:
        posts = pickle.load(rbf)
        for post in posts:
            question = post['Body']
            answers = [item['Body'] for item in post['Answers']]
            ret.extend(_generate_data_from_sentence(
                question, post['Id'], target_doc))
            for answer in answers:
                ret.extend(_generate_data_from_sentence(
                    answer, post['Id'], target_doc))
    # 因为文件太大了所以决定直接分着存储吧。。。
    with open(os.path.join(EZA_PIPELINE_DATA_STORE_PATH[JAVADOC_GLOBAL_NAME], str(index) + EZA_PIPELINE_INPUT_FILE_NAME), 'w', encoding='utf-8') as wf:
        wf.writelines([json.dumps(d) + '\n' for d in ret])


def generate_EZA_pipeline_data_for_javadoc():
    '''
    专门生成javadoc对应的EZA pipeline处理数据
    '''
    javadoc_so_post_filenames = os.listdir(SO_POSTS_STORE_PATH['<java>'])
    i = 1
    for filename in tqdm(javadoc_so_post_filenames):
        transfer_posts2EZAdata(
            os.path.join(SO_POSTS_STORE_PATH['<java>'], filename), i,
            JAVADOC_GLOBAL_NAME
        )
        i += 1


if __name__ == "__main__":
    # 后续可以加个分支处理别的文档
    generate_EZA_pipeline_data_for_javadoc()
