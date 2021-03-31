import os
import pickle

from tqdm import tqdm
from ..config import SO_POSTS_STORE_PATH, JAVADOC_GLOBAL_NAME, DOC_NAME_TO_SO_TAG
from gensim.utils import simple_preprocess
from gensim.models.doc2vec import TaggedDocument
from ..utils import get_html_text_except_code

def so_doc2vec_corpus(doc_name=JAVADOC_GLOBAL_NAME):
    filenames = os.listdir(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]])
    i = 0
    for filename in filenames:
        with open(os.path.join(SO_POSTS_STORE_PATH[DOC_NAME_TO_SO_TAG[doc_name]], filename), "rb") as rbf:
            partial_posts = pickle.load(rbf)
            for thread in tqdm(partial_posts):
                question_body = get_html_text_except_code(thread['Body'])
                yield TaggedDocument(simple_preprocess(question_body), [i])
                i += 1
                for answer in thread['Answers']:
                    answer_body = get_html_text_except_code(answer['Body'])
                    yield TaggedDocument(simple_preprocess(answer_body), [i])
                    i += 1
