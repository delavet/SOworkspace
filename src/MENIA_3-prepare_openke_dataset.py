import random
import networkx as nx

from collections import OrderedDict
from util.constant import *
from util.config import OPENKE_ENTITY2ID_STORE_PATH, OPENKE_RELATION2ID_STORE_PATH, OPENKE_TRAIN2ID_STORE_PATH, OPENKE_TEST2ID_STORE_PATH, OPENKE_VALID2ID_STORE_PATH, JAVADOC_GLOBAL_NAME, LATEST_COMMUNITY_MAP_PATH, LATEST_CONCEPT_MAP_PATH
'''
为了通过API之间的关系推荐API post学习序列，需要通过图嵌入模型训练所有API的图嵌入（以判断API之间关系的密切程度）
通过concept map和community map两个map结合来生成图嵌入训练的数据集
使用openke进行训练，openke位于服务器/media/dell/disk/yinh/torch/OpenKE
生成数据集之后需要到该目录下进行图嵌入模型的训练
'''


def generate_openke_dataset(doc_name: str = JAVADOC_GLOBAL_NAME):
    concept_map = nx.read_gexf(LATEST_CONCEPT_MAP_PATH[doc_name])
    community_map = nx.read_gexf(LATEST_COMMUNITY_MAP_PATH[doc_name])
    entity2id = OrderedDict()
    relation2id = OrderedDict()
    i = 0
    for entity in concept_map.nodes:
        if NodeAttributes.Ntype not in concept_map.nodes[entity].keys():
            continue
        '''
        # 原先寻思着排除module、package等高阶的entity来着，后来寻思着还是加上吧
        if concept_map.nodes[entity][NodeAttributes.Ntype] in high_level_node_types:
            continue
        '''
        entity2id[entity] = i
        i += 1
    d = EdgeType.__dict__
    edge_types = [d[key] for key in d if "__" not in key]
    i = 0
    for relation in edge_types:
        relation2id[relation] = i
        i += 1
    valid_entities = set(entity2id.keys())
    train2id = []
    for api1, api2 in concept_map.edges():
        if api1 not in valid_entities or api2 not in valid_entities:
            continue
        try:
            relation_id = relation2id[concept_map[api1]
                                      [api2][EdgeAttrbutes.Etype]]
        except:
            continue
        id1 = entity2id[api1]
        id2 = entity2id[api2]
        train2id.append([id1, id2, relation_id])
    for api1, api2 in community_map.edges():
        if api1 not in valid_entities or api2 not in valid_entities:
            continue
        try:
            relation_id = relation2id[community_map[api1]
                                      [api2][EdgeAttrbutes.Etype]]
        except:
            continue
        id1 = entity2id[api1]
        id2 = entity2id[api2]
        train2id.append([id1, id2, relation_id])
    random.shuffle(train2id)
    with open(OPENKE_ENTITY2ID_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_e:
        wf_e.write(str(len(entity2id.keys())) + '\n')
        wf_e.writelines([str(entity) + '\t' + str(i) +
                         '\n' for entity, i in entity2id.items()])
    with open(OPENKE_RELATION2ID_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_r:
        wf_r.write(str(len(relation2id.keys())) + '\n')
        wf_r.writelines([str(relation) + '\t' + str(i) +
                         '\n' for relation, i in relation2id.items()])
    with open(OPENKE_TRAIN2ID_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_train, open(OPENKE_VALID2ID_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_valid, open(OPENKE_TEST2ID_STORE_PATH[doc_name], 'w', encoding='utf-8') as wf_test:
        valid_split_index = len(train2id) - 1000
        test_split_index = len(train2id) - 2000
        final_train2id = train2id[:test_split_index]
        test2id = train2id[test_split_index:valid_split_index]
        valid2id = train2id[valid_split_index:]
        wf_train.write(str(len(final_train2id)) + '\n')
        wf_train.writelines([str(item[0]) + '\t' + str(item[1]) +
                             '\t' + str(item[2]) + '\n' for item in final_train2id])
        wf_valid.write(str(len(valid2id)) + '\n')
        wf_valid.writelines([str(item[0]) + '\t' + str(item[1]) +
                             '\t' + str(item[2]) + '\n' for item in valid2id])
        wf_test.write(str(len(test2id)) + '\n')
        wf_test.writelines([str(item[0]) + '\t' + str(item[1]) +
                            '\t' + str(item[2]) + '\n' for item in test2id])


if __name__ == "__main__":
    generate_openke_dataset(JAVADOC_GLOBAL_NAME)
