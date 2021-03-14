import os
import json
import pickle

from tqdm import tqdm
from util.config import JAVADOC_GLOBAL_NAME, SO_POSTS_SEGMENT_INFO_STORE_PATH, SO_POSTS_STORE_PATH, DOC_NAME_TO_SO_TAG


def generate_so_posts_segment_info(doc_name: str = JAVADOC_GLOBAL_NAME):
    segment_info = {}
    so_post_filenames = os.listdir(
        SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]])
    for filename in tqdm(so_post_filenames):
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]], filename), 'rb') as rbf:
            partial_posts = list(pickle.load(rbf))
        for i, thread in enumerate(partial_posts):
            segment_info[thread["Id"]] = [filename, i]
    with open(SO_POSTS_SEGMENT_INFO_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        json.dump(segment_info, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_so_posts_segment_info(JAVADOC_GLOBAL_NAME)
