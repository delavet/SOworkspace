import json
import os
import numpy as np

from tqdm import tqdm
from collections import OrderedDict
from util.apidoc_search.vector_util import VectorUtil
from gensim.models.doc2vec import Doc2Vec
from util.config import JAVADOC_GLOBAL_NAME, API_THREAD_ID_MAP_STORE_PATH, API_THREAD_ID_RESORT_MAP_STORE_PATH, SO_DOC2VEC_MODEL_STORE_PATH, APIDOC_DESCRIPTION_STORE_PATH, base_dir
from util.community_info.so_thread_info_center import ThreadInfoCenter
from util.utils import get_html_text_except_code

with open(os.path.join(base_dir, '/data/howto_kw.txt'), 'r', encoding='utf-8') as rf:
    howto_kws = set([kw.strip() for kw in rf.readlines()]) #howto型帖子关键词表

def resort_api_thread_id_map(doc_name=JAVADOC_GLOBAL_NAME):
    thread_info_center = ThreadInfoCenter(doc_name)
    doc2vec_model = Doc2Vec.load(SO_DOC2VEC_MODEL_STORE_PATH[doc_name])
    vector_tool = VectorUtil(doc2vec_model)
    with open(API_THREAD_ID_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_thread_id_map = json.load(rf)
    with open(APIDOC_DESCRIPTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_descriptions = json.load(rf)
    api_thread_resort_map = OrderedDict()
    itms = list(api_thread_id_map.items())
    all_threads_set = set()
    print("collecting details")
    for api, thread_ids in tqdm(itms):
        all_threads_set.update(thread_ids)
    all_threads = thread_info_center.batch_get_thread_detail_info(list(all_threads_set))
    id2thread_detail = {}
    for th in tqdm(all_threads):
        id2thread_detail[str(th['Id'])] = th
    print("resorting")
    for api, thread_ids in tqdm(itms):
        description_html = api_descriptions.get(api, '')
        desc_vec = vector_tool.get_html_doc2vec_vector(description_html)
        thread_details = [id2thread_detail[id] for id in thread_ids]
        thread_vecs = []
        howto_scores = [] # 计算帖子中是否包含howto型帖子的关键词，如果包含直接一个词加100分，保证其排在最前面
        new_thread_ids = []
        for thread in thread_details:
            new_thread_ids.append(thread['Id'])
            title = thread['Title']
            thread_doc = title + ' '
            question = get_html_text_except_code(thread['Body'])
            thread_doc += question
            '''
            # 20210401:这里之前用第一个回答计算thread doc，之后改成问题的doc试一试
            answers = thread['Answers']
            if len(answers) > 0:
                first_ans_doc = get_html_text_except_code(answers[0]['Body'])
                thread_doc += first_ans_doc
            '''
            thread_vec = vector_tool.get_doc2vec_vector(thread_doc)
            thread_vecs.append(thread_vec)
            howto_score = 0
            for kw in howto_kws:
                if kw in title or kw in question:
                    howto_score += 100
            howto_scores.append(howto_score)
        similarities = VectorUtil.cosine_similarities(np.array(desc_vec), np.array(thread_vecs))
        similarities = [i + j for i, j in zip(similarities, howto_scores)]
        sorted_ids_with_similarities = sorted(zip(new_thread_ids, similarities), key=lambda x: x[1], reverse=True)
        sorted_ids = [item[0] for item in sorted_ids_with_similarities]
        api_thread_resort_map[api] = sorted_ids
    with open(API_THREAD_ID_RESORT_MAP_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(api_thread_resort_map, wf, indent=2, ensure_ascii=False)

    
if __name__ == "__main__":
    resort_api_thread_id_map(JAVADOC_GLOBAL_NAME)
