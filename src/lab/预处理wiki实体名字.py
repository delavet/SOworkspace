import os
import sys
import pickle

'''
先尝试纯文本化方法
'''
WIKIPEDIA_CONCEPT_STORE_PATH = 'C:/workspace/SOworkspace/data/wikipedia_concepts/text_content/'
stemmed_wiki_descriptions_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, 'stemmed/stemmed.txt')
#先把所有wikipedia的概念存起来
pure_wiki_concept_word_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, 'wikipedia_concept_words.pkl')

with open(stemmed_wiki_descriptions_path, 'r', encoding='utf-8') as rf, open(pure_wiki_concept_word_path, 'wb') as wf:
    wiki_concept_words = []
    while True:
        text_line = rf.readline()
        if text_line:
            concept_word = str(text_line).split('|||')[0].strip()
            wiki_concept_words.append(concept_word)
            print("\r",len(wiki_concept_words), concept_word,end="",flush=True)
        else:
            break
    pickle.dump(wiki_concept_words, wf)