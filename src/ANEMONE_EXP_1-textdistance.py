import os
import json
import textdistance

from tqdm import tqdm
from util.config import ANEMONE_DATASET_STORE_PATH, JAVADOC_GLOBAL_NAME, ANEMONE_BERT_TEST_SET_FILE_NAME
from sklearn.metrics import f1_score, precision_score, recall_score
from util.nel.common import longest_common_subsequence

with open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], 'entity_gt_map.json'), 'r', encoding="utf-8") as wf_gt:
    entity_gt_map = json.load(wf_gt)

# DL = textdistance.DamerauLevenshtein()
threshold = 0.9


def dataloader(data_path):
    with open(data_path, "r", encoding='utf-8') as rf:
        for line in rf:
            obj = json.loads(line)
            yield obj


def model(data):
    global DL
    mention = data.get('mention', '').lower()
    entity = data.get('entity', '').lower()
    dis = longest_common_subsequence(mention, entity)
    sim = dis / float(len(mention))
    return sim


def validate(val_dataloader, is_test = True):
    pred = []
    label = []
    raw_pred = []
    mentions = []
    entities = []
    thread_ids = []
    for case in tqdm(val_dataloader):
        try:
            prediction = model(case)
        except:
            print('batch infer failed')
            continue
        pred.append(0 if prediction < threshold else 1)
        label.append(case['label'])
        raw_pred.append(prediction)
        mentions.append(case['mention'])
        entities.append(case['entity'])
        thread_ids.append(case['thread_id'])
    
    if is_test:
        with open('../data/cache/anemone_textdist_pred.json', 'w', encoding='utf-8') as pred_f:
            json.dump(raw_pred, pred_f, ensure_ascii=False, indent=2)
    
    print("first to go real validate: ", get_f1_score_first_to_go(
        raw_pred, label, mentions, entities, thread_ids))
    print("max score real validate: ", get_f1_score_max_score(
        raw_pred, label, mentions, entities, thread_ids))
    return precision_score(label, pred), recall_score(label, pred), f1_score(label, pred)


def get_f1_score_max_score(pred, label, mentions, entities, thread_ids):
    '''
    采用预测分数最大的entity为预测结果的预测方式计算出来的f1
    '''
    mention_predicts = {}
    for i in range(len(pred)):
        mention_key = '_'.join([thread_ids[i], mentions[i]])
        mention_predicts[mention_key] = ['', -1]
    for i in range(len(pred)):
        mention_key = '_'.join([thread_ids[i], mentions[i]])
        if pred[i] < threshold:
            continue
        else:
            if pred[i] > mention_predicts[mention_key][1]:
                mention_predicts[mention_key] = [entities[i], pred[i]]
    total = len(list(mention_predicts.keys()))
    hits = 0
    reject_predict = 0
    for k in mention_predicts.keys():
        if k not in entity_gt_map.keys():
            continue
        if mention_predicts[k][1] == -1:
            reject_predict += 1
        if mention_predicts[k][0] == entity_gt_map[k]:
            hits += 1
    p = hits / (total + 1e-20)
    r = hits / (total - reject_predict + 1e-20)
    f = p
    return p, r, f


def get_f1_score_first_to_go(pred, label, mentions, entities, thread_ids):
    '''
    采用第一个预测大于0.5的entity为预测结果的预测方式计算出来的f1
    '''
    mention_predicts = {}
    for i in range(len(pred)):
        mention_key = '_'.join([thread_ids[i], mentions[i]])
        mention_predicts[mention_key] = ['', -1]
    for i in range(len(pred)):
        mention_key = '_'.join([thread_ids[i], mentions[i]])
        if mention_predicts[mention_key][1] == -1:
            if pred[i] > threshold:
                mention_predicts[mention_key] = [entities[i], pred[i]]

    total = len(list(mention_predicts.keys()))
    hits = 0
    reject_predict = 0
    for k in mention_predicts.keys():
        if k not in entity_gt_map.keys():
            continue
        if mention_predicts[k][1] == -1:
            reject_predict += 1
        if mention_predicts[k][0] == entity_gt_map[k]:
            hits += 1
    p = hits / (total - reject_predict + 1e-20)
    r = hits / (total + 1e-20)
    f = p
    return p, r, f


def test():
    test_dataloader = dataloader(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_BERT_TEST_SET_FILE_NAME))
    precision, recall, f1 = validate(test_dataloader)
    print('precision: %.4f' % precision)
    print('recall: %.4f' % recall)
    print('f1-score: %.4f' % f1)
    

if __name__ == "__main__":
    test()
