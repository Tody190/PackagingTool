# coding=utf-8
__author__ = 'yangtao'
__version__ = '0.1'


ascii_cat = \
r"""
  ,-.       _,---._ __  / \
 /  )    .-'       `./ /   \
(  (   ,'            `/    /|
 \  `-"             \'\   / |
  `.              ,  \ \ /  |
   /`.          ,'-`----Y   |
  (            ;        |   '
  |  ,-.    ,-'         |  /
  |  | (   |            | /  author: yangtao
  )  |  \  `.___________|/  enjoy it!
  `--'   `--'
"""

def show(author=None, version=None):
    print(ascii_cat)
    if author:
        print("author: %s"%author)
    if version:
        print("version: %s"%version)
    print("enjoy it!")
    print('')