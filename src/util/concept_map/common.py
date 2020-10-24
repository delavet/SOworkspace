import re
import logging
import networkx as nx
from selenium.common.exceptions import NoSuchElementException
from ..config import *


def get_relative_path_from_href(href):
    try:
        match = re.search(r'(?<=javadocs/).*$', href)
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