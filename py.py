code = """
import os
import ast

PI = 3.14

class Parser:
    ...

def tokenize(x):
    ...

def parse():
    ...

if __name__ == "__main__":
    ..."""

from ast import parse, dump, get_source_segment

tree = parse(code)
# print(tree._fields)
# print(tree.body[4].args._fields)
# print(get_source_segment(code, tree.body[0]), tree.body[0].col_offset, tree.body[0].end_col_offset+1)
# for node in tree.body:
#     print('source',get_source_segment(code, node))
#     print('len',len(get_source_segment(code, node)))

#     print('start:', node.col_offset)
#     print('start:', node.end_col_offset)
#     print('='*40)

print("import os"[0:9])