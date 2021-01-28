from .config import *
from bs4 import BeautifulSoup


def get_all_indexes(sub: str, s: str):
    '''
    在父字符串中查找所有子字符串出现的首尾位置
    ## parameter
    `sub` : 子字符串
    `s` : 父字符串
    '''
    ret = []
    start_from_index = 0
    while start_from_index < len(s):
        sub_begin_index = s.find(sub, start_from_index)
        if sub_begin_index == -1:
            break
        sub_end_index = sub_begin_index + len(sub) - 1
        # 判断识别出来的是不是个夹在一个单词里的子串而不是真的一个词
        if sub_begin_index > 0 and s[sub_begin_index - 1].isalnum():
            start_from_index = sub_end_index + 1
            continue
        if sub_end_index < len(s) - 1 and s[sub_end_index + 1].isalnum():
            start_from_index = sub_end_index + 1
            continue
        ret.append([sub_begin_index, sub_end_index])
        start_from_index = sub_end_index + 1
    return ret


def get_html_text_except_code(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for pre in soup.find_all('pre'):
        pre.extract()
    return soup.text
