from os import lseek
import numpy as np

from gensim.models import FastText, Word2Vec
from .config import *
from bs4 import BeautifulSoup


def get_all_indexes(sub: str, s: str):
    '''
    在父字符串中查找所有子字符串出现的首尾位置
    ## parameter
    `sub` : 子字符串
    `s` : 父字符串
    '''
    ret = []
    start_from_index = 0
    while start_from_index < len(s):
        sub_begin_index = s.find(sub, start_from_index)
        if sub_begin_index == -1:
            break
        sub_end_index = sub_begin_index + len(sub) - 1
        # 判断识别出来的是不是个夹在一个单词里的子串而不是真的一个词
        if sub_begin_index > 0 and s[sub_begin_index - 1].isalnum():
            start_from_index = sub_end_index + 1
            continue
        if sub_end_index < len(s) - 1 and s[sub_end_index + 1].isalnum():
            start_from_index = sub_end_index + 1
            continue
        ret.append([sub_begin_index, sub_end_index])
        start_from_index = sub_end_index + 1
    return ret


def get_html_text_except_code(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for pre in soup.find_all('pre'):
        pre.extract()
    return soup.text


def single_line_print(to_print):
    print("\r", to_print, end="", flush=True)


def sigmoid(x: float):
    return 1.0 / (1 + np.exp(-x))


def normalize(x):
    if x is None:
        x = 0
    return sigmoid(float(x))


def get_api_name_from_entity_id(entity_id: str):
    '''
    concept map中API的ID经常带api和html等无用信息，所以就去掉一下
    '''
    ret = entity_id.replace('.html', '').replace('api/', '')
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    return ret


def get_api_qualified_name_from_entity_id(entity_id: str):
    '''
    生成比上面更正经的，可以和复旦的concept map匹配的api信息
    '''
    ret = entity_id.replace('.html', '').replace('api/', '')
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    ret = ret.replace('&lt;', '<')
    ret = ret.replace('&gt;', '>')
    tokens = ret.split('/')
    if len(tokens) == 1:
        return ret
    if '.' in tokens[0]:
        tokens = tokens[1:]
    ret = '.'.join(tokens)
    ret = ret.replace('#', '.')
    return ret


def get_api_qualified_name_from_entity_id_without_parameter(entity_id: str):
    '''
    生成API的qualified name
    与get_api_qualified_name_from_entity_id的区别是去掉了name后面的参数部分，方便判断两个API是重载的函数
    '''
    ret = entity_id.replace('.html', '').replace('api/', '')
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    ret = ret.replace('&lt;', '<')
    ret = ret.replace('&gt;', '>')
    tokens = ret.split('/')
    if len(tokens) == 1:
        return ret
    if '.' in tokens[0]:
        tokens = tokens[1:]
    ret = '.'.join(tokens)
    ret = ret.replace('#', '.')
    # 删除method的参数列表，只留方法名
    bracket_index_1 = ret.find('<')
    bracket_index_2 = ret.find('(')
    bracket_index_3 = ret.find('[')
    l = [i for i in [bracket_index_1, bracket_index_2, bracket_index_3] if i != -1]
    if len(l) == 0:
        l.append(-1)
    bracket_index = min(l)
    if bracket_index != -1:
        ret = ret[:bracket_index]
    return ret


def get_api_extreme_short_name_from_entity_id(entity_id: str):
    '''
    生成API的最短描述字符串，如方法名或类名、包名
    ## 注意：可能有重名的情况发生
    '''
    ret = entity_id.replace('.html', '').replace('api/', '')
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    ret = ret.replace('&lt;', '<')
    ret = ret.replace('&gt;', '>')
    tokens = ret.split('/')
    ret = tokens[-1]
    sharp_index = ret.find('#')
    if sharp_index != -1:
        ret = ret[sharp_index + 1:]
    # 删除method的参数列表，只留方法名
    bracket_index = ret.find('<')
    if bracket_index == -1:
        bracket_index = ret.find('(')
    if bracket_index == -1:
        bracket_index = ret.find('[')
    if bracket_index != -1:
        ret = ret[:bracket_index]
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


def get_apidoc_wiki_embedding_model(doc_name=JAVADOC_GLOBAL_NAME):
    '''
    获取从api文档与wiki联合训练的embedding model
    ## 20210326
    目前用的fasttext
    '''
    return FastText.load(APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH[doc_name])


def get_node2vec_model(doc_name=JAVADOC_GLOBAL_NAME):
    '''
    获取文档图谱的node2vec model
    '''
    return Word2Vec.load(NODE2VEC_MODEL_STORE_PATH[doc_name])
