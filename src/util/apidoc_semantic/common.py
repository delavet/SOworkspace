import re
import spacy

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

__lemmatizer = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
__parser = spacy.load('en_core_web_sm', disable=['ner'])
TERM_STOPLIST = set(stopwords.words('english'))


def preprocess(sentence: str) -> str:
    '''
    预处理一句话将其变为能够训练的语料

    ## Return

    以空格分隔的、完成了lemmatize的字符串语句
    '''
    global __lemmatizer
    processed_doc = __lemmatizer(sentence)
    return ' '.join(' '.join([token.lemma_ for token in processed_doc if not token.is_stop]).split())


def extract_noun_chunks(sentence: str) -> str:
    global __parser
    doc = __parser(sentence)
    ret = []
    for chunk in doc.noun_chunks:
        chunk_arr = []
        if len(chunk) == 0:
            continue
        for token in chunk:
            if token.is_stop:
                continue
            chunk_arr.append(token.lemma_)
        chunk_lemma = " ".join(chunk_arr)
        ret.append(chunk_lemma.lower())
    return ret


def pre_tokenize(text: str) -> str:
    '''
    预先以CamelCase和下划线分隔来处理句子，返回分隔后的句子
    '''
    # text = ' '.join([token.lower() if token.isupper() else token for token in ])
    ret = ''
    for i in range(len(text)):
        ch = text[i]
        latterCh = text[i+1] if i < len(text) - 1 else ''
        if ch.isupper() and latterCh.isalpha() and not latterCh.isupper():
            ret += ' ' + ch
        elif ch == '_' or ch == '-':
            ret += ' '
        else:
            ret += ch
    return ret.strip()


def extract_sentences_from_desc_html(desc_html: str):
    '''
    从以html格式表示的api文档描述中分离出单独的句子
    '''
    soup = BeautifulSoup(desc_html, 'lxml')
    for pre in soup.find_all('pre'):
        pre.extract()
    pat = re.compile('<[^>]+>', re.S)
    sentences = pat.sub('', soup.text)
    sentences = [' '.join([t for t in sent.split() if t != ' '])
                 for sent in sent_tokenize(sentences)]
    return sentences


def extract_sentences_from_plain_text(text: str):
    '''
    从纯文本中分离单独的句子
    '''
    sentences = [' '.join([t for t in sent.split() if t != ' ']).strip()
                 for sent in sent_tokenize(text)]
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
    if len(term) <= 2 or term.isdigit() or (len(term) > 20 and len(term.split()) > 3):
        return False
    prefix, *rest = term.lower().split()
    if prefix in TERM_STOPLIST:
        return False
    return True
