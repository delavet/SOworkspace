import re
import logging
import networkx as nx
from selenium.common.exceptions import NoSuchElementException
from util.concept_map.common import get_latest_concept_map
from util.constant import *
from util.nel.common import api_url_match
from elasticsearch import Elasticsearch
from util.config import APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH, JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port, HYBRID_WORD2VEC_CORPUS_STORE_PATH
from pprint import pprint
#from util.mysql_access.posts import DBPosts
from util.utils import get_api_qualified_name_from_entity_id
from util.apidoc_search.vector_util import VectorUtil
import numpy as np
from util.apidoc_search.api_search_service import ApiSearchService


def get_relative_path_from_href(href):
    '''
    去除超链接中的冗余内容，获取每个超链接对应的API相对链接
    目前写死了对应的javadoc，需要后续改进
    '''
    try:
        match = re.search(f'(?<=api/).*$', href)
    except Exception as e:
        logging.exception(e)
        raise NoSuchElementException()
    if match is not None:
        ret = match.group()
    else:
        ret = href
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    return ret


def pre_tokenize(text: str):
    text = ' '.join([token.lower() if token.isupper()
                     else token for token in text.split(' ')])
    ret = ''
    for i in range(len(text)):
        ch = text[i]
        latterCh = text[i+1] if i < len(text) - 1 else ''
        if ch.isupper() and latterCh.isalpha() and not latterCh.isupper():
            ret += ' ' + ch.lower()
        elif ch == '_':
            ret += ' '
        else:
            ret += ch
    return ret


if __name__ == "__main__":
    '''concept_map = get_latest_concept_map()
    Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
    module_nodes = [
        node for node in concept_map.nodes if node in Ntype_attributes and (Ntype_attributes[node] == NodeType.MODULE or Ntype_attributes[node] == NodeType.PACKAGE)]
    print(len(module_nodes))
    print(module_nodes)'''
    '''
    print(api_url_match(
        "file:///F:/SOworkspace/apidocs/javadocs/api/java.net.http/java/net/http/package-summary.html",
        "http://docs.oracle.com/javase/6/docs/api/java/net/http/package-summary.html"
    ))
    '''

    es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)
    query_body = {
        'query': {
            'match': {
                'name': {
                    'query': 'exists'
                }
            }
        },
    }
    res = es.search(index=JAVADOC_GLOBAL_NAME, body=query_body)
    pprint(res)

    '''
    x = [[1,2,3], [2,3,4]]
    y = VectorUtil.get_weight_mean_vec(x)
    print(y)
    '''
    '''
    new_lines = []
    with open(HYBRID_WORD2VEC_CORPUS_STORE_PATH[JAVADOC_GLOBAL_NAME], 'r', encoding='utf-8') as rf:
        for line in rf:
            new_lines.append(' '.join(line.split()).strip() + '\n')
    with open(HYBRID_WORD2VEC_CORPUS_STORE_PATH[JAVADOC_GLOBAL_NAME], 'w', encoding='utf-8') as wf:
        wf.writelines(new_lines)
    '''

    '''
    vector_util = VectorUtil(APIDOC_WIKI_FASTTEXT_MODEL_STORE_PATH[JAVADOC_GLOBAL_NAME])
    print(vector_util.get_word_similarity('array', 'arrays'))
    print(vector_util.get_word_similarity('array', 'awt'))
    print(vector_util.get_word_similarity('matrix', 'image'))
    '''
    '''
    service = ApiSearchService(JAVADOC_GLOBAL_NAME)
    print('initilalized!')
    pprint(service.search_by_concept('network security'))
    pprint(service.search_literally('FIFO collection'))
    pprint(service.search_by_concept('network security'))
    pprint(service.search_by_concept('paint lines on whiteboard'))
    pprint(service.search_by_concept('unique item collection'))
    pprint(service.search_by_concept('concurrent linked list'))
    '''

    # print(DBPosts().get_thread_info_by_ids("9395808,9396545"))
    # print(get_api_qualified_name_from_entity_id('api/jdk.security.auth/com/sun/security/auth/NTUserPrincipal.html#&lt;init&gt;(java.lang.String)'))
