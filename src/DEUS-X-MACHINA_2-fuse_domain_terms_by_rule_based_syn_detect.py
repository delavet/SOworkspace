import json

from util.apidoc_semantic.common import valid_term
from util.apidoc_semantic.term_fusion import Fusion
from util.config import APIDOC_DESCRIPTION_STORE_PATH, JAVADOC_GLOBAL_NAME, INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH, API_DOMAIN_TERM_STORE_PATH, FUSED_API_DOMAIN_TERM_MAP_STORE_PATH, FUSED_DOMAIN_TERM_API_MAP_STORE_PATH, FUSED_DOMAIN_TERM_STORE_PATH


def fuse_domain_terms_by_rule_based_syns_detect(doc_name: str = JAVADOC_GLOBAL_NAME):
    with open(API_DOMAIN_TERM_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        not_fused_terms = json.load(rf)
    new_terms = []
    for term in not_fused_terms:
        if valid_term(term):
            new_terms.append(term)
    not_fused_terms = set(new_terms)
    term_fusion = Fusion()
    synsets = term_fusion.fuse(not_fused_terms)
    fused_term_to_aliases_map = {}
    fused_alias_to_term_map = {}
    for synset in synsets:
        k = synset.key
        fused_term_to_aliases_map[k] = list(synset.terms)
        for t in synset.terms:
            fused_alias_to_term_map[t] = k
    # fused_terms = fused_term_to_aliases_map.keys()
    with open(FUSED_DOMAIN_TERM_STORE_PATH, 'w', encoding='utf-8') as wf:
        json.dump(fused_term_to_aliases_map, wf, ensure_ascii=False, indent=2)
    with open(INITIAL_API_DOMAIN_TERM_MAP_STORE_PATH, 'r', encoding='utf-8') as rf:
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
                fused_api_to_term_map[term].append(api_name)
            else:
                fused_api_to_term_map[term] = [api_name]
    with open(FUSED_API_DOMAIN_TERM_MAP_STORE_PATH, 'w', encoding='utf-8') as wf_api_term, open(FUSED_DOMAIN_TERM_API_MAP_STORE_PATH, 'w', encoding='utf-8') as wf_term_api:
        json.dump(fused_api_to_term_map, wf_api_term)
        json.dump(fused_term_to_api_map, wf_term_api)


if __name__ == "__main__":
    fuse_domain_terms_by_rule_based_syns_detect(JAVADOC_GLOBAL_NAME)
