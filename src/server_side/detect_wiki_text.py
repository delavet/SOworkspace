import os
import sys
import pickle
from gensim.parsing.porter import PorterStemmer
from gensim.utils import tokenize
from tqdm import tqdm

WIKIPEDIA_CONCEPT_STORE_PATH = 'wikipedia'
stemmed_wiki_descriptions_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, r'C:\workspace\SOworkspace\data\wikipedia_concepts\text_content\stemmed\stemmed.txt')
#先把所有wikipedia的概念存起来
pure_wiki_concept_word_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, r'C:\workspace\SOworkspace\data\wikipedia_concepts\text_content\wikipedia_concept_words.pkl')
with open(pure_wiki_concept_word_path, 'rb') as rf:
    wiki_concept_words = pickle.load(rf)
wiki_concept_words = set(wiki_concept_words)

javadoc_description_path = r'C:\workspace\SOworkspace\data\apidoc_description\javadoc_descriptions.pkl'
with open(javadoc_description_path, 'rb') as rf:
    javadoc_description = pickle.load(rf)

javadoc_wiki_concept_path = r'C:\workspace\SOworkspace\data\wikipedia_concepts\text_content\javadoc_wiki_concepts_pure_text.pkl'

javadoc_concepts = {}
cnt = 0
stemmer = PorterStemmer()
for concept, description in tqdm(javadoc_description.items()):
    #cnt += 1
    #print("\r",cnt,end="",flush=True)
    processed_desc = [stemmer.stem(word) for word in tokenize(description)]
    temp_words = []
    for word in processed_desc:
        if word in wiki_concept_words and word != '':
            temp_words.append(word)
    javadoc_concepts[concept] = temp_words
with open(javadoc_wiki_concept_path, 'wb') as wf:
    pickle.dump(javadoc_concepts, wf)
    