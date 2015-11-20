
from functools import *

# for later
def of(type, x):
    return isinstance(x, type)

# hierarhy root
class Ast:
    pass

# empty list
class Nil(Ast):
    def __init__(me, info):
        me.info = info

    def __str__(me):
        return "()"

class Var(Ast):
    def __init__(me, info, name):
        me.info = info
        me.name = name

    def __str__(me):
        # for debug reasons
        return "$" + me.name

class Const(Ast):
    def __init__(me, info, value):
        me.info  = info
        me.value = value

    def __str__(me):
        # for debug reasons
        return "#" + str(me.value)

class Function(Ast):
    def __init__(me, info, args, body):
        me.info = info
        me.args = args
        me.body = body

    def __str__(me):
        return "(" + unwords(me.args) + " -> " + str(me.body) + ")"

class App(Ast):
    def __init__(me, info, f, xs):
        me.info = info
        me.f    = f
        me.xs   = xs

    def __str__(me):
        return "(" + str(me.f) + " " + unwords(me.xs) + ")"

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwords(lst):
    add = lambda x, y: x + " " + y if x else y
    return str(reduce(add, map(str, lst), ""))

class LetExpr(Ast):
    def __init__(me, info, name, value, context):
        me.info    = info
        me.name    = name
        me.value   = value
        me.context = context

    def __str__(me):
        return "let " + me.name + " = " + str(me.value) + " in\n" + str(me.context)

class LetRecExpr(Ast):
    def __init__(me, info, name, value, context):
        me.info    = info
        me.name    = name
        me.value   = value
        me.context = context

    def __str__(me):
        return "let-rec " + me.name + " = " + str(me.value) + " in\n" + str(me.context)

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwordsWith(sep, lst):
    add = lambda x, y: x + " " + sep + " " + y if x else y
    return str(reduce(add, map(str, lst), ""))

class DataDecls(Ast):
    def __init__(me, info, decls, context):
        me.info    = info
        me.decls   = decls
        me.context = context

    def __str__(me):
        return "data " + unwordsWith("\nand", me.decls) + " in\n" + str(me.context)

class DataType(Ast):
    def __init__(me, info, name, ctors):
        me.info  = info
        me.name  = name
        me.ctors = ctors

    def __str__(me):
        return me.name + " = " + unwordsWith("or", me.ctors)

class DataCtor(Ast):
    def __init__(me, info, name, dtors):
        me.info  = info
        me.name  = name
        me.dtors = dtors

    def __str__(me):
        return me.name + " " + unwords(me.dtors)

def constant(x):
    return lambda *_: x
