from util.mysql_access.posts import DBPosts
from util.config import SO_POSTS_STORE_PATH

import pickle
import os


def collect_so_posts_related_to(tag_name):
    '''
    ## collect all so posts that related to a tag
    the tag may mostly be a language, but there may be some other usage
    ### parameter: `tag_name`:
        the tag's name, which is a 'tag' such as '<java>' not just 'java'
    '''
    posts_db = DBPosts()
    cnt = 0
    so_posts_to_store = []
    for item in posts_db.collect_posts_by_tag(tag_name):
        so_posts_to_store.append(item)
        if len(so_posts_to_store) >= 50000:
            file_name = f"posts_{cnt}.pkl"
            file_store_path = os.path.join(SO_POSTS_STORE_PATH[tag_name], file_name)
            with open(file_store_path, 'wb') as wbf:
                pickle.dump(so_posts_to_store, wbf)
            del so_posts_to_store
            so_posts_to_store = []
            cnt += 1
            print("\r",f"{cnt * 50000} posts stored",end="",flush=True)
    if len(so_posts_to_store) > 0:
        file_name = f"posts_{cnt}.pkl"
        file_store_path = os.path.join(SO_POSTS_STORE_PATH[tag_name], file_name)
        with open(file_store_path, 'wb') as wbf:
            pickle.dump(so_posts_to_store, wbf)
        del so_posts_to_store
        cnt += 1
    print("\r","done!",end="",flush=True)


if __name__ == "__main__":
    collect_so_posts_related_to('<java>')

    