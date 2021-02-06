import linecache
import sys


if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print('请输入文件路径和文件起止行数作为参数！')
        print('###usage:')
        print('python show_large_text_file.py filename 1 100')
    filename = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    for i in range(start, end + 1):
        print(linecache.getline(filename, i))
