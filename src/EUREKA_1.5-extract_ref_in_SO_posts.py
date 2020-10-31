from os import link
from util.config import SO_POSTS_STORE_PATH, TEMP_FILE_STORE_PATH
from tqdm import tqdm
from bs4 import BeautifulSoup

import pickle
import os


def extract_references_from_posts(so_record_file_path):
    with open(so_record_file_path, "rb") as rbf:
        so_post_list = pickle.load(rbf)
    with open(so_record_file_path, "wb") as wbf:
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
            links = [s.get('href') for s in link_soups]
            post['Links'] = links
            so_post_with_link_list.append(post)
            whole_links.extend(links)
        pickle.dump(so_post_with_link_list, wbf)
    return whole_links
        #pickle.dump(whole_links, link_wbf)


if __name__ == "__main__":
    files = os.listdir(SO_POSTS_STORE_PATH['<java>'])
    all_links = []
    for i in range(len(files)):
        links = extract_references_from_posts(os.path.join(SO_POSTS_STORE_PATH['<java>'], f'posts_{i}.pkl'))
        all_links.extend(links)
    with open(os.path.join(TEMP_FILE_STORE_PATH, 'java_so_posts_links.pkl'), 'wb') as wbf:
        pickle.dump(all_links, wbf)

    

