from lark import Lark
from lark.tree import Tree
from lark.lexer import Token
from Transformer import MediatorTransformer
import json

def tree_to_dict(tree):
    if isinstance(tree, Tree):  # 使用导入的 Tree 类
        return {
            "data": tree.data,
            "children": [tree_to_dict(child) for child in tree.children]
        }
    elif isinstance(tree, Token):
        return {
            "type": tree.type,
            "value": tree.value
        }
    else:
        return tree

def pre_parse(test_code): 
    with open('Grammar.lark', 'r', encoding='utf-8') as grammar_file:
        mediator_grammar = grammar_file.read()
    parser = Lark(mediator_grammar, parser='lalr')
    return parser.parse(test_code)
    
def parse(test_code): 
    with open('grammar.lark', 'r', encoding='utf-8') as grammar_file:
        mediator_grammar = grammar_file.read()
    parser = Lark(mediator_grammar, parser='lalr', transformer=MediatorTransformer())
    return parser.parse(test_code)