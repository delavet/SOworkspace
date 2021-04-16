from util.constant import EdgeAttrbutes, EdgeType, NodeAttributes
from util.utils import get_api_qualified_name_from_entity_id
from .common import api_url_match, camel_case_split, longest_common_subsequence
from ..concept_map.common import get_latest_concept_map
from elasticsearch import Elasticsearch
from util.config import Elasticsearch_host, Elasticsearch_port
from util.constant import high_level_node_types

import networkx as nx
import re


concept_map = get_latest_concept_map()
Ntype_attributes = nx.get_node_attributes(concept_map, 'Ntype')
href_attributes = nx.get_node_attributes(concept_map, 'local_href')
api_entities = [
    node for node in concept_map if node in Ntype_attributes and node in href_attributes]

es = Elasticsearch(hosts='localhost', port=9200)
splitters = set(
    [
        ",",
        ".",
        "/",
        ";",
        "'",
        "`",
        "\\",
        "[",
        "]",
        "<",
        ">",
        "?",
        ":",
        '"',
        "{",
        "}",
        "~",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "(",
        ")",
        "-",
        "=",
        "_",
        "+",
        "，",
        "。",
        "、",
        "；",
        "‘",
        "’",
        "【",
        "】",
        "·",
        "！",
        "…",
        "（",
        "）",
    ])


def get_gt_candidate(mention: str, ground_truth_url: str):
    '''
    根据SO帖子中天然的ground-truth，搜索图得到对应的链接实体
    ## parameter
    `mention` : 帖子中对API的提及文本
    `ground_truth_url` : mention对应的超链接url
    '''
    global api_entities
    global href_attributes
    for entity in api_entities:
        if api_url_match(href_attributes[entity], ground_truth_url):
            return entity
    return None


def simple_candidate_selector(mention: str):
    '''
    简单的候选实体查找器，查找规则：
    ```
    实体的正式名字和mention的最长公共子序列长度达到mention长度的40%以上
    ```
    实验证明这玩意太慢了
    '''
    global api_entities
    select_threshold = 0.3
    for entity in api_entities:
        if longest_common_subsequence(entity, mention) >= select_threshold * len(mention):
            yield entity


def substring_candidate_selector(mention: str):
    '''
    根据子串出现的候选实体查找器，查找规则：
    ```
    mention中的一个单词出现在了实体名字中
    ```
    '''
    global api_entities
    splitter_pattern = r'[;,\.\s/_\-\(\)\[\]\{\}#]'
    temp_tokens = re.split(splitter_pattern, mention)
    tokens = []
    for token in temp_tokens:
        tokens.extend(camel_case_split(token))
    for entity in api_entities:
        if any([token for token in tokens if token in entity.lower()]):
            yield entity


def tokenize(text: str):
    raw_tokens = []
    cur_index = 0
    cur_token = ""
    while cur_index < len(text):
        cur_ch = text[cur_index]
        if cur_ch in splitters:
            if len(cur_token) > 0:
                raw_tokens.append(cur_token)
            raw_tokens.append(cur_ch)
            cur_token = ""
            cur_index += 1
        elif re.search(r"^\s$", cur_ch) is not None:
            if len(cur_token) > 0:
                raw_tokens.append(cur_token)
            cur_token = ""
            cur_index += 1
        else:
            cur_token = cur_token + cur_ch
            cur_index += 1
    if len(cur_token) > 0:
        raw_tokens.append(cur_token)
    return [token for token in raw_tokens if token != '' and ' ' not in token]


def match_even_one_token(mention: str, entity_name: str):
    '''
    判断mention中是不是至少有一个token是和实体名对应的
    因为原始数据中出现了一些写着用什么method但是引用却是类的引用的情况，所以用这个使得数据集更加整齐一些
    '''
    tokens = [t.lower() for t in tokenize(mention)]
    name = get_api_qualified_name_from_entity_id(entity_name).lower()
    return any([t for t in tokens if t in name])


def search_for_possible_ground_truth_entity(mention: str, orignal_ground_truth_entity: str):
    '''
    一开始抽取出的NEL ground_truth可能不靠谱
    可能有链接是类但是mention是类中方法的情况
    所以如果grount truth匹配失败就试着上他的成员里寻找新的ground truth
    '''
    succes = list(concept_map.adj[orignal_ground_truth_entity])
    for entity in succes:
        if concept_map[orignal_ground_truth_entity][entity][EdgeAttrbutes.Etype] == EdgeType.INCLUDE and match_even_one_token(mention, entity):
            return entity
    return None


def es_search(term: str, search_attr: str, fuzziness=None):
    global es
    query_obj = {
        'query': term
    }
    if fuzziness is not None:
        query_obj['fuzziness'] = fuzziness
    query_body = {
        'query': {
            'match': {
                search_attr: query_obj
            }
        },
    }
    es_res = es.search(index='javadoc', filter_path='hits.hits._source.node_name',
                       body=query_body)
    if len(es_res.keys()) == 0:
        return []
    ret = [item['_source']['node_name'] for item in es_res['hits']['hits']]
    return ret


def es_wildcard_search(term: str, search_attr: str):
    global es
    query_body = {
        'query': {
            'wildcard': {
                search_attr: {
                    'value': f"*{term}*"
                }
            }
        },
    }
    es_res = es.search(index='javadoc', filter_path='hits.hits._source.node_name',
                       body=query_body)
    if len(es_res.keys()) == 0:
        return []
    ret = [item['_source']['node_name'] for item in es_res['hits']['hits']]
    return ret


def es_candidate_selector(mention: str):
    '''
    基于elastic search模糊匹配的候选实体查找器
    '''
    mention_tokens = tokenize(mention)
    search_term = ' '.join(mention_tokens).lower()

    res = es_search(search_term, 'name', 'auto')
    for candidate in res:
        yield candidate
    res = es_search(search_term, 'description', 'auto')
    for candidate in res:
        yield candidate
    res = []
    for token in mention_tokens:
        if any([s for s in splitters if s in token]):
            continue
        res.extend(es_wildcard_search(token, 'name'))
    for candidate in res:
        yield candidate
    for token in mention_tokens:
        if any([s for s in splitters if s in token]):
            continue
        res.extend(es_wildcard_search(token, 'description'))
    for candidate in res:
        yield candidate
    return res


def es_candidate_strict_selector(mention: str):
    '''
    基于elastic search严格匹配的候选实体查找器
    ## 2021.4.14只在API的名字中做candidate的搜索，而且此时使用的elasticsearch是由ZAMPATHA 1.1生成的，API名是非常短的，只包含必要信息
    '''
    mention_tokens = tokenize(mention)
    search_term = ' '.join(mention_tokens).lower()

    res = es_search(search_term, 'name')
    for candidate in res:
        yield candidate


def entity_is_high_level(entity):
    return concept_map.nodes[entity].get(NodeAttributes.Ntype, '') in high_level_node_types
