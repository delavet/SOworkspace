import pickle
import sys
from pprint import pprint
from typing import OrderedDict


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('请输入pkl文件路径作为参数！')
    arg = sys.argv[1]
    with open(arg, "rb") as rbf:
        data = pickle.load(rbf)
        if isinstance(data, dict):
            print("检测到dict，输出前10项")
            pprint(list(data.items())[:10])
        elif isinstance(data, list):
            print("检测到list，输出前10项")
            pprint(data[:10])
        elif isinstance(data, set):
            print("检测到set，输出前10条")
            pprint(list(data)[:10])
        else:
            print("不知道是啥对象，直接输出了")
            pprint(data)
