import re

from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup


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
