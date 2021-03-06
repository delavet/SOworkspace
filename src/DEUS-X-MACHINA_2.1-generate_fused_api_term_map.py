import json

from util.config import APIDOC_DESCRIPTION_STORE_PATH, JAVADOC_GLOBAL_NAME, INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH, API_DOMAIN_TERM_STORE_PATH, FUSED_API_DOMAIN_TERM_MAP_STORE_PATH, FUSED_DOMAIN_TERM_API_MAP_STORE_PATH, FUSED_DOMAIN_TERM_STORE_PATH


def generate_fused_api_term_map(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(FUSED_DOMAIN_TERM_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        fused_term_to_aliases_map = json.load(rf)
    fused_alias_to_term_map = {}
    for k, aliases in fused_term_to_aliases_map.items():
        for alias in aliases:
            fused_alias_to_term_map[alias] = k
    print('len of whole initially fused terms: ',
          len(fused_term_to_aliases_map.keys()))
    with open(INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        initial_api_term_map = json.load(rf)
    fused_term_to_api_map = {}
    fused_api_to_term_map = {}
    for api_name, initial_terms in initial_api_term_map.items():
        correspond_fused_terms = set()
        for term in initial_terms:
            correspond_fused_term = fused_alias_to_term_map.get(term, None)
            if correspond_fused_term is not None:
                correspond_fused_terms.add(correspond_fused_term)
        fused_api_to_term_map[api_name] = list(correspond_fused_terms)
        for term in correspond_fused_terms:
            if term in fused_term_to_api_map:
                fused_term_to_api_map[term].append(api_name)
            else:
                fused_term_to_api_map[term] = [api_name]
    with open(FUSED_API_DOMAIN_TERM_MAP_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_api_term, open(FUSED_DOMAIN_TERM_API_MAP_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_term_api:
        json.dump(fused_api_to_term_map, wf_api_term,
                  ensure_ascii=False, indent=2)
        json.dump(fused_term_to_api_map, wf_term_api,
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    generate_fused_api_term_map()
