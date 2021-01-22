import networkx as nx
from ...concept_map.common import get_latest_concept_map
from ..common import min_edit_distance
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


porter = PorterStemmer()


def normalize(value: float, min_val: float, max_val: float) -> float:
    if min_val > max_val:
        return 0
    normalized_value = value
    if value < min_val:
        normalized_value = min_val
    if value > max_val:
        normalized_value = max_val
    return min_val + (normalized_value - min_val) / (max_val - min_val)


def feature_extract__edit_distance(mention: str, entity: str) -> float:
    '''
    提取特征：mention和entity的编辑距离，归一化到0-20
    '''
    distance = min_edit_distance(mention.lower(), entity.lower())
    return normalize(distance, 0, 20)


def feature_extract__context_cooccur(mention_context: str, entity_context: str) -> float:
    '''
    提取特征：mention和context的上下文中共同出现的词
    '''
    global porter
    mention_filtered = set([porter.stem(word.lower()) for word in word_tokenize(
        mention_context) if word.lower() not in stopwords.words('english')])
    entity_filtered = set([porter.stem(word.lower()) for word in word_tokenize(
        entity_context) if word.lower() not in stopwords.words('english')])
    intersection_set = mention_filtered.intersection(entity_filtered)
    return normalize(len(intersection_set), 0, 50)
