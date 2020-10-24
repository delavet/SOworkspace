import os
import sys
import pickle

WIKIPEDIA_CONCEPT_STORE_PATH = 'C:/workspace/SOworkspace/data/wikipedia_concepts/text_content/'
stemmed_wiki_descriptions_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, 'stemmed/stemmed.txt')
#先把所有wikipedia的概念存起来
pure_wiki_concept_word_path = os.path.join(WIKIPEDIA_CONCEPT_STORE_PATH, 'wikipedia_concept_words.pkl')
with open(pure_wiki_concept_word_path, 'rb') as rf:
    wiki_concept_words = pickle.load(rf)
    len(wiki_concept_words)

javadoc_description_path = 'C:/workspace/SOworkspace/data/apidoc_description/javadoc_descriptions.pkl'
with open(javadoc_description_path, 'rb') as rf:
    javadoc_description = pickle.load(rf)

javadoc_wiki_concept_path = 'C:/workspace/SOworkspace/data/apidoc_description/javadoc_wiki_concepts_pure_text.pkl'
from tqdm import tqdm
javadoc_concepts = {}
for concept, description in tqdm(javadoc_description.items()):
    temp_words = []
    for word in wiki_concept_words:
        if word in description:
            temp_words.append(word)
    javadoc_concepts[concept] = temp_words
with open(javadoc_wiki_concept_path, 'wb') as wf:
    pickle.dump(javadoc_concepts, wf)
    