import json
from tqdm import tqdm


'''
ANEMONE的初版预测有很多很乐观的完全预测错了的情况
在新的结果跑出来之前，先用启发式方式对这个第一版结果筛选一下，防止结果太烂
'''
whole_simple_prediction_store_dir = 'C:/workspace/服务器备份/ANEMONE/whole_simple_prediction/'
whole_simple_prediction_file_path = f'{whole_simple_prediction_store_dir}all_predictions.json'


def ANEMONE_predictions_match(mention: str, api: str):
    '''
    判断预测出来的mention和api是不是大概率是预测对了
    '''
    mention_tokens = [token.lower() for token in mention.split(
        ' ') if token.isalpha() and len(token) > 2]
    api = api.lower()
    min_match_tokens = len(mention_tokens) // 2 + 1 if len(
        mention_tokens) <= 3 else len(mention_tokens) // 2 + 2  # 启发式规则
    if min_match_tokens == 0:
        min_match_tokens = 1
    match = 0
    for token in mention_tokens:
        if token in api:
            match += 1
        elif token.endswith('s') and token[:len(token) - 1] in api:
            match += 1
    return match >= min_match_tokens


def filter_whole_predictions(whole_simple_prediction_file_path: str, filterd_path: str):
    with open(whole_simple_prediction_file_path, 'r', encoding='utf-8') as rf, open(filterd_path, 'w', encoding='utf-8') as wf:
        predictions = json.load(rf)
        counter = 0
        filterd_predictions = {}
        for thread_id, preds in tqdm(predictions.items()):
            filterd = {}
            for mention, api in preds.items():
                if ANEMONE_predictions_match(mention, api):
                    filterd[mention] = api
                    counter += 1
            if len(filterd.keys()) <= 0:
                continue
            filterd_predictions[thread_id] = filterd
        print("data amount: ", counter)
        print('thread count: ', len(filterd_predictions))
        json.dump(filterd_predictions, wf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    filtered_path = f'{whole_simple_prediction_store_dir}filterd_predictions.json'
    filter_whole_predictions(whole_simple_prediction_file_path, filtered_path)
