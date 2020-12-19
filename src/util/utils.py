from .config import *


def get_all_indexes(sub : str, s : str):
    '''
    在父字符串中查找所有子字符串出现的首尾位置
    ## parameter
    `sub` : 子字符串
    `s` : 父字符串
    '''
    ret = []
    start_from_index = 0
    while start_from_index < len(s):
        sub_begin_index = s.find(sub,start_from_index)
        if sub_begin_index == -1:
            break
        sub_end_index = sub_begin_index + len(sub) - 1
        ret.append([sub_begin_index, sub_end_index])
        start_from_index = sub_end_index + 1
    return ret