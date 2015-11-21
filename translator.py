
from functools import *
from operator import *

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
    "_": "hole"
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

print(convert_name("<STDIN?>._."))