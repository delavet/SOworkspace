from util.config import SO_POSTS_STORE_PATH, EUREKA_DATASET_STORE_PATH, EUREKA_FULL_DATASET_FILE_NAME, JAVADOC_GLOBAL_NAME, APIDOC_ROOT_URL, EUREKA_TRAIN_SET_FILE_NAME, EUREKA_TEST_SET_FILE_NAME

import os
import json
import random

'''
EUREKA-2.5
分割一下EUREKA 2生成的NER数据集，分成训练集和测试集
'''


def split_ner_train_test_set(dataset_path: str):
    '''
    分割某个数据集为测试集和训练集
    ## Parameter
    `dataset_path` : 数据集文件存储目录的路径，没有包括文件名
    '''
    with open(os.path.join(dataset_path, EUREKA_FULL_DATASET_FILE_NAME), 'r', encoding="utf-8") as rf, open(os.path.join(dataset_path, EUREKA_TRAIN_SET_FILE_NAME), "w", encoding="utf-8") as wf_train, open(os.path.join(dataset_path, EUREKA_TEST_SET_FILE_NAME), "w", encoding="utf-8") as wf_test:
        data_lines = rf.readlines()
        random.shuffle(data_lines)
        split_index = len(data_lines) - len(data_lines) // 20
        # split_index = len(data_lines) - 1000
        train_data_lines = data_lines[:split_index]
        test_data_lines = data_lines[split_index:]
        wf_train.writelines(train_data_lines)
        wf_test.writelines(test_data_lines)


if __name__ == "__main__":
    split_ner_train_test_set(EUREKA_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME])
