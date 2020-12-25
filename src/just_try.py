from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import pickle
import json
def extract_references_from_posts(so_record_file_path):
    with open(so_record_file_path, "rb") as rbf:
        so_post_list = pickle.load(rbf)
        so_post_with_link_list = []
        whole_links = []
        for post in so_post_list:
            question_body = post['Body']
            answers = post['Answers']
            question_soup = BeautifulSoup(question_body, 'lxml')
            link_soups = []
            link_soups.extend(question_soup.find_all('a'))
            for answer in answers:
                answer_soup = BeautifulSoup(answer['Body'], 'lxml')
                link_soups.extend(answer_soup.find_all("a"))
            links = [s.text for s in link_soups if 'docs.oracle.com' in str(s.get('href')) and 'api' in str(s.get('href'))]
            whole_links.extend(links)
    return whole_links


files = os.listdir('C:/workspace/SOworkspace/data/so_posts/java/')
a_dict = { }
for i in tqdm(range(len(files))):
    links = extract_references_from_posts(os.path.join('C:/workspace/SOworkspace/data/so_posts/java/', f'posts_{i}.pkl'))
    for a in links:
        if a.lower() in a_dict.keys():
            a_dict[a.lower()] = a_dict[a.lower()] + 1
        else:
            a_dict[a.lower()] = 1

with open(os.path.join('C:/workspace/SOworkspace/data/cache/', 'java_so_posts_a_texts.json'), 'w', encoding='utf-8') as wf:
    json.dump(sorted([item for item in a_dict.items() if item[1] > 10], key=lambda x:x[1], reverse=True), wf)