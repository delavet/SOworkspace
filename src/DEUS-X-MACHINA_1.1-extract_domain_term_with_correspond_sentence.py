import json

from tqdm import tqdm
from util.apidoc_semantic.common import extract_sentences_from_desc_html
from util.apidoc_semantic.domain_term_extractor import EntityExtractor
from util.config import APIDOC_DESCRIPTION_STORE_PATH, JAVADOC_GLOBAL_NAME, INITIAL_API_DOMAIN_TERM__SENTENCE_MAP_STORE_PATH, API_DOMAIN_TERM_STORE_PATH


entity_extractor = EntityExtractor()


def extract_domain_term_with_sentence_from_API_desc(DOC_NAME: str = JAVADOC_GLOBAL_NAME):
    global entity_extractor
    api_desc_path = APIDOC_DESCRIPTION_STORE_PATH[DOC_NAME]
    # 约定api description以json格式存储
    with open(api_desc_path, 'r', encoding='utf-8') as rf:
        api_descriptions = dict(json.load(rf))
    with open(INITIAL_API_DOMAIN_TERM__SENTENCE_MAP_STORE_PATH[DOC_NAME], 'w', encoding='utf-8') as wf:
        api_domain_term_sentence_map = {}
        sentences = []
        for api_name, api_description in tqdm(api_descriptions.items()):
            desc_sentences = extract_sentences_from_desc_html(api_description)
            terms_sentences = []
            for sentence in desc_sentences:
                domain_terms_, code_elements_ = entity_extractor.extract_from_sentence(
                    sentence)
                sentences.append(sentence)
                for term in domain_terms_:
                    terms_sentences.append([term, len(sentences) - 1])
            api_domain_term_sentence_map[api_name] = terms_sentences
        json.dump([api_domain_term_sentence_map, sentences],
                  wf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    extract_domain_term_with_sentence_from_API_desc(JAVADOC_GLOBAL_NAME)
