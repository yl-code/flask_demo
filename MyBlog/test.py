import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(basedir)
print(os.path.dirname(__file__))  # 返回上一层目录，__file__表示当前文件
print(__file__)
