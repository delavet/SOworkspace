import json
import matplotlib.pyplot as plt
import numpy as np

from util.config import base_dir


def statistic_textbook_apperance():
    text_static_store_path = f'{base_dir}/data/exp/textbook_record.json'
    community_record_path = f'{base_dir}/data/exp_whole/community_record_thres_90_res_0.1.json'
    exist_in_book = 0
    exist_in_book_ratios = []
    same_chap_ratios = []
    x = []
    colors = []
    labels = []
    max_diffs = []
    with open(text_static_store_path, "r", encoding='utf-8') as rf, open(community_record_path, "r", encoding='utf-8') as rf2:
        textbook_records = json.load(rf)
        community_records = json.load(rf2)
    for community_id, textbook_record in textbook_records.items():
        community_record = community_records[community_id]
        for page in textbook_record['pages']:
            x.append(page)
            colors.append(int(community_id))
            labels.append(community_id)
        if textbook_record['exist'] == 0:
            continue
        exist_in_book += 1
        max_diffs.append(
            max(textbook_record['pages']) - min(textbook_record['pages']))
        if len(community_record) <= 3:
            continue
        rate = float(textbook_record['exist']) / float(len(community_record))
        exist_in_book_ratios.append(rate)
        same_chap_rate = float(
            textbook_record['sameChap']) / float(textbook_record['exist'])
        same_chap_ratios.append(same_chap_rate)
    print(exist_in_book)
    print(np.mean(exist_in_book_ratios))
    print(np.mean(same_chap_ratios))
    print(max_diffs)
    print(np.mean(max_diffs))
    y = colors
    sizes = [10] * len(x)
    for i in range(47):
        plt.axhline(i, ls="--", lw=0.5, c='black')
    plt.scatter(x, y, c=colors, s=sizes, marker='o', cmap='tab20')
    plt.xlabel("page number")
    plt.ylabel("learning entry index")
    
    # plt.legend()
    plt.savefig(
        f'{base_dir}/data/exp_whole/textbook.png', bbox_inches='tight', dpi=500)


if __name__ == "__main__":
    statistic_textbook_apperance()
