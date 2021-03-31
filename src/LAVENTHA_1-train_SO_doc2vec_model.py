from gensim.models.doc2vec import Doc2Vec
from util.config import JAVADOC_GLOBAL_NAME, SO_DOC2VEC_MODEL_STORE_PATH
from util.so_semantic.so_corpus import so_doc2vec_corpus

'''
LAVENTHA：API-THREAD MAP纪录的重新排序推荐机制
因为系统的链接预测误差以及某些API关联的thread过多，可能造成了一些API与并不是那么相关的thread连了起来，且与单个API相连的thread过多
第一版的LAVENTHA使用了doc2vec，判断每个thread title + 第一个回答组成的doc与API描述之间的doc2vec相关性，并依此为所有相关的thread进行重新排序
'''


def train_SO_doc2vec(doc_name=JAVADOC_GLOBAL_NAME):
    model = Doc2Vec(vector_size=200, min_count=2, epochs=4)
    train_corpus = so_doc2vec_corpus(doc_name)
    print('building vocabularies')
    model.build_vocab(train_corpus)
    print('vocabularies built')
    print('training')
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)
    print('trained')
    print('saving')
    model.save(SO_DOC2VEC_MODEL_STORE_PATH[doc_name])
    print('saved')


if __name__ == "__main__":
    train_SO_doc2vec(JAVADOC_GLOBAL_NAME)