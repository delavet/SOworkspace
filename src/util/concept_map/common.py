import re
import logging
import networkx as nx
from selenium.common.exceptions import NoSuchElementException
from ..config import *


def get_relative_path_from_href(href):
    '''
    去除超链接中的冗余内容，获取每个超链接对应的API相对链接
    目前写死了对应的javadoc，需要后续改进
    '''
    try:
        match = re.search(f'(?<=javadocs/).*$', href)
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


def get_latest_concept_map(doc_name = 'javadoc'):
    graph_path = LATEST_CONCEPT_MAP_PATH[doc_name]
    return nx.read_gexf(graph_path)
    

if __name__ == "__main__":
    print(get_relative_path_from_href("file:///F:/SOworkspace/apidocs/javadocs/api/java.net.http/java/net/http/package-summary.html"))
    print(get_relative_path_from_href("www.baidu.com"))