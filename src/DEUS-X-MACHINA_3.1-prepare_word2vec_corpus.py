import json
import wikipedia
import networkx as nx

from tqdm import tqdm
from wikipedia.wikipedia import page
from util.config import JAVADOC_GLOBAL_NAME, HYBRID_WORD2VEC_CORPUS_STORE_PATH, APIDOC_DESCRIPTION_STORE_PATH, WIKIDUMP_PATH, FUDAN_CONCEPT_MAP_PATH
from util.apidoc_semantic.common import extract_sentences_from_desc_html, extract_sentences_from_plain_text, preprocess, pre_tokenize
from util.utils import single_line_print

'''
为训练query-文档语义匹配而进行Word2vec的语料准备
语料为文档描述和wiki描述的混合语料
每一行是一个句子，经过去停用词和lemma化处理，以空格分隔
'''

def prepare_word2vec_corpus_from_doc(wf, doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(APIDOC_DESCRIPTION_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        api_descriptions = json.load(rf)
    print('preparing doc dataset')
    for desc in tqdm(api_descriptions.values()):
        sentences = [preprocess(pre_tokenize(sentence)) + '\n'
                     for sentence in extract_sentences_from_desc_html(desc)]
        wf.writelines(sentences)
    print('doc dataset prepared')


def prepare_word2vec_corpus_from_wikiV2(wf, doc_name: str= JAVADOC_GLOBAL_NAME):
    print('preparing wiki dataset')
    fudan_concept_map = nx.read_gpickle(FUDAN_CONCEPT_MAP_PATH[doc_name])
    fudan_wiki_nodes = set(
        [node for node in fudan_concept_map if 'wikidata' in fudan_concept_map.nodes[node]['labels']])
    cnt = 1
    for node in tqdm(fudan_wiki_nodes):
        properties = fudan_concept_map.nodes[node]['properties']
        name = properties.get('wikidata_name', None)
        if name is None:
            name = properties.get('name', None)
        if name is None:
            name = properties.get('labels_en', None)
        if name is None:
            continue
        try:
            page = wikipedia.page(name)
        except:
            single_line_print(f'failed to find page: {name}')
            continue
        cnt += 1
        sentences = [preprocess(pre_tokenize(sentence)) + '\n'
                     for sentence in extract_sentences_from_plain_text(page)]
        wf.writelines(sentences)
    print('wiki dataset prepared!')
        

def prepare_word2vec_corpus_from_wiki(wf, doc_name: str = JAVADOC_GLOBAL_NAME):
    '''
    过慢，废弃
    '''
    print('preparing wiki dataset')
    article_indexes = set()
    fudan_concept_map = nx.read_gpickle(FUDAN_CONCEPT_MAP_PATH[doc_name])
    fudan_wiki_nodes = set(
        [node for node in fudan_concept_map if 'wikidata' in fudan_concept_map.nodes[node]['labels']])
    wiki_titles = set()
    for node in fudan_wiki_nodes:
        properties = fudan_concept_map.nodes[node]['properties']
        name = properties.get('wikidata_name', None)
        if name is None:
            name = properties.get('name', None)
        if name is None:
            name = properties.get('labels_en', None)
        if name is None:
            continue
        wiki_titles.add(name.lower())
    print('start detecting wiki articles')
    with open(WIKIDUMP_PATH['title'], 'r', encoding='utf-8') as rf_title:
        for i, line in tqdm(enumerate(rf_title)):
            single_line_print(f'article line: {i}')
            line = line.strip()
            if line.lower() not in wiki_titles:
                continue
            article_indexes.add(i)
    print(f'{len(article_indexes)} wiki articles detected')
    index = -1
    current_article = ''
    with open(WIKIDUMP_PATH['article'], 'r', encoding='utf-8') as rf_article:
        for line in rf_article:
            if line.startswith('#Article:'):
                index += 1
                single_line_print(f'article line: {index}')
                if current_article != '':
                    sentences = [preprocess(pre_tokenize(sentence)) + '\n'
                                 for sentence in extract_sentences_from_plain_text(current_article)]
                    wf.writelines(sentences)
                    current_article = ''
            elif line.startswith('#'):
                continue
            elif index in article_indexes:
                current_article = current_article + line
    print('wiki dataset prepared')      
    

def prepare_word2vec_corpus(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(HYBRID_WORD2VEC_CORPUS_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf:
        prepare_word2vec_corpus_from_doc(wf, doc_name)
        prepare_word2vec_corpus_from_wikiV2(wf, doc_name)


if __name__ == "__main__":
    prepare_word2vec_corpus(JAVADOC_GLOBAL_NAME)
