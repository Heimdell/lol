
from functools import *
from operator import *

from ast import *

known_ops = {
    "+": "plus",
    "@": "doge",
    "$": "swag",
    "-": "minus",
    "*": "milt",
    "/": "div",
    "|": "stick",
    "?": "wat",
    ">": "more",
    "<": "less",
    "_": "hole",
    ".": "dude"
}

def convert_char(char):
    if char in known_ops:
        return "_" + known_ops[char]
    
    if char >= 'A' and char <= 'z':
        return char

    return "_" + str(ord(char))

safe = lambda op: lambda x, y: op(x, y) if x else y

def convert_name(name):
    return reduce(safe(add), map(convert_char, name))

def convert_ast(ast):
    if of(Nil, ast):
        return "[]";
    
    if of(Var, ast):
        return convert_name(ast.name)
    
    if of(Const, ast):
        if of(str, ast.value):
            return ast.value + '\"'
        return str(ast.value)

    if of(Function, ast):
        return (
              "function (" + unwordsWith(",", ast.args)
            + ") { return " + convert_ast(ast.body) 
            + " }"
        )

    if of(App, ast):
        return convert_ast(ast.f) + "(" + unwordsWith(",", map(convert_ast, ast.xs)) + ")"

    if of(LetExpr, ast):
        return ( 
              "(function (" + ast.name 
            + ") { return " + convert_ast(ast.context) 
            + " }) (" + convert_ast(ast.value)
            + ")"
        )

    raise "Can't do anything with " + str(ast)

def convert(ast):
    runtime = open("runtime.js").read()

    return runtime + "\n\nvar it = " + convert_ast(ast)

