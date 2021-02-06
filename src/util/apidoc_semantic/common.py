import re
import spacy

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

__lemmatizer = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
TERM_STOPLIST = set(stopwords.words('english'))


def extract_sentences_from_desc_html(desc_html: str):
    '''
    从以html格式表示的api文档描述中分离出单独的句子
    '''
    soup = BeautifulSoup(desc_html, 'lxml')
    for pre in soup.find_all('pre'):
        pre.extract()
    pat = re.compile('<[^>]+>', re.S)
    sentences = pat.sub('', soup.text)
    sentences = [' '.join(sent.split()) for sent in sent_tokenize(sentences)]
    return sentences


def lemmatize(doc: str):
    global __lemmatizer
    processed_doc = __lemmatizer(doc)
    return " ".join([token.lemma_ for token in processed_doc])


def valid_term(term):
    '''
    简单判断抽取出来的term是否合乎要求
    因为各种奇怪的东西都会抽出来……
    '''
    global TERM_STOPLIST
    term = str(term)
    if len(term) <= 2 or term.isdigit() or (len(term) > 30 and len(term.split()) > 4):
        return False
    prefix, *rest = term.split()
    if prefix in TERM_STOPLIST:
        return False
    return True
