from gensim.models import FastText
from gensim.models.word2vec import LineSentence
from util.config import JAVADOC_GLOBAL_NAME, APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH, HYBRID_WORD2VEC_CORPUS_STORE_PATH


def train_fasttext_model(doc_name: str = JAVADOC_GLOBAL_NAME):
    print('start training')
    fasttext_model = FastText(corpus_file=HYBRID_WORD2VEC_CORPUS_STORE_PATH[doc_name], min_count=1, workers=12)
    print('end_training')
    print('try an vector of "array"')
    print(fasttext_model.wv['array'])
    fasttext_model.save(APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH[doc_name])


if __name__ == "__main__":
    train_fasttext_model(JAVADOC_GLOBAL_NAME)
