import re
import logging
import networkx as nx
from selenium.common.exceptions import NoSuchElementException
from util.concept_map.common import get_latest_concept_map
from util.constant import *
from util.nel.common import api_url_match
# from elasticsearch import Elasticsearch
from util.config import JAVADOC_GLOBAL_NAME, Elasticsearch_host, Elasticsearch_port
from pprint import pprint
from util.mysql_access.posts import DBPosts


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
    '''
    es = Elasticsearch(hosts=Elasticsearch_host, port=Elasticsearch_port)
    query_body = {
        'query': {
            'wildcard': {
                'name': {
                    'value': '*arraylist*'
                }
            }
        },
    }
    res = es.search(index=JAVADOC_GLOBAL_NAME, filter_path='hits.hits._source.description',
                    body=query_body)
    pprint(res)
    '''
    print(DBPosts().get_thread_info_by_ids("9395808,9396545"))
