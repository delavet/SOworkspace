import re
import os
import pickle
import json

from tqdm import tqdm
from util.config import APIDOC_API_URL_REGEX_PATTERN, JAVADOC_GLOBAL_NAME, SO_POSTS_STORE_PATH, DOC_NAME_TO_SO_TAG, EXP_DEUS_X_MACHINA_EXP_CANDIDATE_THREADS_STORE_PATH

'''
从整个thread的数据中找寻有可能作为search部分实验的候选对象
大致要求：
    1. thread只引用了一个文档中的API
    2. 标题中有how to的优先选择
'''


def generate_DXM_exp_thread_candidates(doc_name: str):
    result = []
    filenames = os.listdir(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]])
    for filename in tqdm(filenames):
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]], filename), 'rb') as rbf:
            partial_threads = pickle.load(rbf)
            result.extend([thread for thread in partial_threads
                           if thread['Title'].lower().startswith('how to')
                           and len(
                               [link for link in thread['Links'] if re.search(
                                   APIDOC_API_URL_REGEX_PATTERN[JAVADOC_GLOBAL_NAME], str(link)) is not None]
                           ) == 1])
    print(f'found {len(result)} candidates')
    with open(EXP_DEUS_X_MACHINA_EXP_CANDIDATE_THREADS_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(result, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_DXM_exp_thread_candidates(JAVADOC_GLOBAL_NAME)
