import json

from tqdm import tqdm
from util.apidoc_semantic.common import extract_sentences_from_desc_html
from util.apidoc_semantic.domain_term_extractor import EntityExtractor
from util.config import APIDOC_DESCRIPTION_STORE_PATH, JAVADOC_GLOBAL_NAME, INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH, API_DOMAIN_TERM_STORE_PATH


entity_extractor = EntityExtractor()


def initial_extract_domain_term_from_API_desc(DOC_NAME: str = JAVADOC_GLOBAL_NAME):
    global entity_extractor
    api_desc_path = APIDOC_DESCRIPTION_STORE_PATH[DOC_NAME]
    # 约定api description以json格式存储
    with open(api_desc_path, 'r', encoding='utf-8') as rf:
        api_descriptions = dict(json.load(rf))
    with open(INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH[DOC_NAME], 'w', encoding='utf-8') as wf_map, open(API_DOMAIN_TERM_STORE_PATH[DOC_NAME], 'w', encoding='utf-8') as wf_terms:
        api_domain_term_map = {}
        domain_terms = set()
        for api_name, api_description in tqdm(api_descriptions.items()):
            desc_sentences = extract_sentences_from_desc_html(api_description)
            terms = set()
            codes = set()
            for sentence in desc_sentences:
                domain_terms_, code_elements_ = entity_extractor.extract_from_sentence(
                    sentence)
                terms.update(domain_terms_)
                codes.update(code_elements_)
            api_domain_term_map[api_name] = list(terms)
            domain_terms.update(terms)

        json.dump(api_domain_term_map, wf_map, ensure_ascii=False, indent=2)
        json.dump(list(domain_terms), wf_terms, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    initial_extract_domain_term_from_API_desc(JAVADOC_GLOBAL_NAME)
