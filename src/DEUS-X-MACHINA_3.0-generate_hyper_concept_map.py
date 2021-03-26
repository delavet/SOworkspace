import json
from re import T
import networkx as nx

from tqdm import tqdm
from util.config import JAVADOC_GLOBAL_NAME, LATEST_HYPER_CONCEPT_MAP_PATH, FUDAN_CONCEPT_MAP_PATH, FUSED_API_DOMAIN_TERM_MAP_STORE_PATH, FUSED_DOMAIN_TERM_STORE_PATH, LATEST_CONCEPT_MAP_PATH
from util.constant import *
from util.utils import get_api_qualified_name_from_entity_id

'''
生成带有domain term和wiki term信息的concept map
'''
def generate_hyper_concept_map(doc_name = JAVADOC_GLOBAL_NAME):
    fudan_concept_map = nx.read_gpickle(FUDAN_CONCEPT_MAP_PATH[doc_name])
    with open(FUSED_API_DOMAIN_TERM_MAP_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        fused_api_domain_term_map = json.load(rf)
    with open(FUSED_DOMAIN_TERM_STORE_PATH[doc_name], 'r', encoding='utf-8') as rf:
        fused_api_term_record = json.load(rf)
    hyper_concept_map = nx.DiGraph(
        nx.read_gexf(LATEST_CONCEPT_MAP_PATH[doc_name]))
    i = 0
    # add domain term nodes
    temp_domain_term2node_id = {}
    for domain_term, aliases in fused_api_term_record.items():
        cur_node_name = f"domain_term_{i}"
        hyper_concept_map.add_node(cur_node_name)
        temp_domain_term2node_id[domain_term] = cur_node_name
        hyper_concept_map.nodes[cur_node_name][NodeAttributes.NAME] = domain_term
        hyper_concept_map.nodes[cur_node_name][NodeAttributes.Ntype] = NodeType.DOMAIN_TERM
        hyper_concept_map.nodes[cur_node_name][NodeAttributes.ALIAS] = list(
            aliases)
        i += 1
    for api, domain_terms in fused_api_domain_term_map.items():
        if api not in hyper_concept_map.nodes:
            print(f'failed to find api {api}')
            continue
        for domain_term in domain_terms:
            term_node_id = temp_domain_term2node_id.get(domain_term, None)
            if term_node_id is None:
                for id in temp_domain_term2node_id.values():
                    node = hyper_concept_map.nodes[id]
                    if domain_term in node[NodeAttributes.ALIAS]:
                        term_node_id = id
                        break
            if term_node_id is None:
                continue
            hyper_concept_map.add_edge(api, term_node_id)
            hyper_concept_map[api][term_node_id][EdgeAttrbutes.Etype] = EdgeType.MENTION
    fudan_wiki_nodes = set(
        [node for node in fudan_concept_map if 'wikidata' in fudan_concept_map.nodes[node]['labels']])
    
    for wiki_node in tqdm(fudan_wiki_nodes):
        if 'properties' not in fudan_concept_map.nodes[wiki_node].keys():
            continue
        cur_wiki_node_id = f'wiki_term_{wiki_node}'
        hyper_concept_map.add_node(cur_wiki_node_id)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.Ntype] = NodeType.WIKI_TERM
        name = None
        properties = fudan_concept_map.nodes[wiki_node]['properties']
        name = properties.get('name', None)
        if name is None:
            name = properties.get('wikidata_name', None)
        if name is None:
            name = properties.get('labels_en', None)
        if name is None:
            continue
        aliases = set()
        aliases_en = properties.get('aliases_en', None)
        if aliases_en is not None:
            aliases.update(aliases_en)
        origin_aliases = properties.get('alias', None)
        if origin_aliases is not None:
            aliases.update(origin_aliases)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.NAME] = name
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.ALIAS] = list(aliases)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.ADDITIONAL_PROPERTIES] = properties
    cnt = 0
    for wiki_node in tqdm(fudan_wiki_nodes):
        cur_wiki_node_id = f'wiki_term_{wiki_node}'
        succes = list(fudan_concept_map.succ[wiki_node])
        preds = list(fudan_concept_map.pred[wiki_node])
        for succ in succes:
            if succ not in fudan_wiki_nodes:
                continue
            wiki_labels = list(fudan_concept_map[wiki_node][succ].keys())
            hyper_concept_map.add_edge(
                cur_wiki_node_id, f'wiki_term_{succ}')
            hyper_concept_map[cur_wiki_node_id][f'wiki_term_{succ}'][EdgeAttrbutes.WIKI_LABEL] = wiki_labels
        
        for pred in preds:
            if 'domain term' not in fudan_concept_map.nodes[pred]['labels']:
                continue
            properties = fudan_concept_map.nodes[pred]['properties']
            fudan_name_set = set()
            try:
                if 'term_name' in properties.keys():
                    fudan_name_set.add(properties['term_name'].lower())
                if 'alias' in properties.keys():
                    fudan_name_set.update([c.lower() for c in properties["alias"]])
                if 'lemma' in properties.keys():
                    fudan_name_set.add(properties['lemma'].lower())
            except:
                pass
            for term_id in temp_domain_term2node_id.values():
                name_set = set()
                name_set.add(hyper_concept_map.nodes[term_id][NodeAttributes.NAME].lower())
                name_set.update(
                    [c.lower() for c in hyper_concept_map.nodes[term_id][NodeAttributes.ALIAS]])
                if not name_set.isdisjoint(fudan_name_set):
                    hyper_concept_map.add_edge(term_id, cur_wiki_node_id)
                    hyper_concept_map[term_id][cur_wiki_node_id][EdgeAttrbutes.Etype] = EdgeType.RELATED_TO
                    cnt += 1
                    break
    print('detect related to for: ', cnt)
    nx.write_gpickle(hyper_concept_map, LATEST_HYPER_CONCEPT_MAP_PATH[doc_name])


def generate_hyper_concept_mapV2(doc_name=JAVADOC_GLOBAL_NAME):
    fudan_concept_map = nx.read_gpickle(FUDAN_CONCEPT_MAP_PATH[doc_name])
    hyper_concept_map = nx.DiGraph(
        nx.read_gexf(LATEST_CONCEPT_MAP_PATH[doc_name]))
    code_element_nodes = [node for node in fudan_concept_map if 'code_element' in fudan_concept_map.nodes[node]['labels'] ]
    qualify_name2api = {}
    for api in hyper_concept_map.nodes:
        qualify_name2api[get_api_qualified_name_from_entity_id(api)] = api
    cnt = 0
    for code_element_node in tqdm(code_element_nodes):
        code_element_name = fudan_concept_map.nodes[code_element_node]['properties'].get('qualified_name', None)
        if code_element_name is None or code_element_name not in qualify_name2api.keys():
            continue
        succes = list(fudan_concept_map.succ[code_element_node])
        for succ in succes:
            if 'domain term' in fudan_concept_map.nodes[succ]['labels']:
                if succ not in hyper_concept_map.nodes:
                    hyper_concept_map.add_node(succ)
                    cnt += 1
                    hyper_concept_map.nodes[succ][NodeAttributes.Ntype] = NodeType.DOMAIN_TERM
                    hyper_concept_map.nodes[succ][NodeAttributes.NAME] = fudan_concept_map.nodes[succ]['properties']['term_name']
                    alias = set()
                    if 'alias' in fudan_concept_map.nodes[succ]['properties'].keys():
                        alias.update(
                            fudan_concept_map.nodes[succ]['properties']['alias'])
                    if 'lemma' in fudan_concept_map.nodes[succ]['properties'].keys():
                        alias.add(
                            fudan_concept_map.nodes[succ]['properties']['lemma'])
                    hyper_concept_map.nodes[succ][NodeAttributes.ALIAS] = list(alias)
                hyper_concept_map.add_edge(qualify_name2api[code_element_name], succ)
                hyper_concept_map[qualify_name2api[code_element_name]][succ][EdgeAttrbutes.Etype] = EdgeType.MENTION
            if 'sentence' in fudan_concept_map.nodes[succ]['labels']:
                sent_succes = fudan_concept_map.succ[succ]
                for sent_succ in sent_succes:
                    if 'domain term' not in fudan_concept_map.nodes[sent_succ]['labels']:
                        continue
                    if sent_succ not in hyper_concept_map.nodes:
                        cnt += 1
                        hyper_concept_map.add_node(sent_succ)
                        hyper_concept_map.nodes[sent_succ][NodeAttributes.Ntype] = NodeType.DOMAIN_TERM
                        hyper_concept_map.nodes[sent_succ][NodeAttributes.NAME] = fudan_concept_map.nodes[sent_succ]['properties']['term_name']
                        alias = set()
                        if 'alias' in fudan_concept_map.nodes[sent_succ]['properties'].keys():
                            alias.update(
                                fudan_concept_map.nodes[sent_succ]['properties']['alias'])
                        if 'lemma' in fudan_concept_map.nodes[sent_succ]['properties'].keys():
                            alias.add(
                                fudan_concept_map.nodes[sent_succ]['properties']['lemma'])
                        hyper_concept_map.nodes[sent_succ][NodeAttributes.ALIAS] = list(
                            alias)
                    hyper_concept_map.add_edge(
                        qualify_name2api[code_element_name], sent_succ)
                    hyper_concept_map[qualify_name2api[code_element_name]
                                      ][sent_succ][EdgeAttrbutes.Etype] = EdgeType.MENTION
    print('detect domain terms: ', cnt)
    fudan_wiki_nodes = set(
        [node for node in fudan_concept_map if 'wikidata' in fudan_concept_map.nodes[node]['labels']])
    for wiki_node in tqdm(fudan_wiki_nodes):
        if 'properties' not in fudan_concept_map.nodes[wiki_node].keys():
            continue
        cur_wiki_node_id = wiki_node
        hyper_concept_map.add_node(cur_wiki_node_id)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.Ntype] = NodeType.WIKI_TERM
        name = None
        properties = fudan_concept_map.nodes[wiki_node]['properties']
        name = properties.get('name', None)
        if name is None:
            name = properties.get('wikidata_name', None)
        if name is None:
            name = properties.get('labels_en', None)
        if name is None:
            continue
        aliases = set()
        aliases_en = properties.get('aliases_en', None)
        if aliases_en is not None:
            aliases.update(aliases_en)
        origin_aliases = properties.get('alias', None)
        if origin_aliases is not None:
            aliases.update(origin_aliases)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.NAME] = name
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.ALIAS] = list(
            aliases)
        hyper_concept_map.nodes[cur_wiki_node_id][NodeAttributes.ADDITIONAL_PROPERTIES] = properties
    cnt = 0
    cnt2 = 0
    for wiki_node in tqdm(fudan_wiki_nodes):
        cur_wiki_node_id = wiki_node
        succes = list(fudan_concept_map.succ[wiki_node])
        preds = list(fudan_concept_map.pred[wiki_node])
        for succ in succes:
            if succ not in fudan_wiki_nodes:
                continue
            wiki_labels = list(fudan_concept_map[wiki_node][succ].keys())
            hyper_concept_map.add_edge(
                cur_wiki_node_id, succ)
            cnt2 += 1
            hyper_concept_map[cur_wiki_node_id][succ][EdgeAttrbutes.WIKI_LABEL] = wiki_labels

        for pred in preds:
            if 'domain term' not in fudan_concept_map.nodes[pred]['labels']:
                continue
            if pred not in hyper_concept_map.nodes:
                continue
            properties = fudan_concept_map.nodes[pred]['properties']
            hyper_concept_map.add_edge(pred, cur_wiki_node_id)
            hyper_concept_map[pred][cur_wiki_node_id][EdgeAttrbutes.Etype] = EdgeType.RELATED_TO
            cnt += 1
        
    print('detect in wiki relation: ', cnt2)
    print('detect related to for: ', cnt)
    nx.write_gpickle(hyper_concept_map,
                     LATEST_HYPER_CONCEPT_MAP_PATH[doc_name])
    
    

if __name__ == "__main__":
    generate_hyper_concept_mapV2(JAVADOC_GLOBAL_NAME)
