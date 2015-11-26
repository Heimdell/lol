
from functools import *
from utils     import *

# hierarhy root
class Ast:
    pass

class Var(Ast):
    def __init__(me, info, name):
        me.info = info
        me.name = name

    def __str__(me):
        # for debug reasons
        return me.name

class Const(Ast):
    def __init__(me, info, value):
        me.info  = info
        me.value = value

    def __str__(me):
        # for debug reasons
        return "<" + str(me.value) + ">"

class App(Ast):
    def __init__(me, info, f, xs):
        me.info = info
        me.f    = f
        me.xs   = xs

    def __str__(me):
        return str(me.f) + "(" + unwordsWith(",", me.xs) + ")"

class LetExpr(Ast):
    def __init__(me, info, bindings, context):
        me.info     = info
        me.bindings = bindings
        me.context  = context

    def __str__(me):
        bindings_text = unwordsWith("\nand", map(vararg(lambda val, args, vararg, value: (
            val + " " + unwords(args) + (" ..." if vararg else "") + " = " + str(value)
        )), me.bindings))
        return "let " + bindings_text + " in\n" + str(me.context)

class Delayed(Ast):
    def __init__(me, info, thunk):
        me.info  = info
        me.thunk = thunk

    def __str__(me):
        return "(\\" + str(me.thunk) + ")"

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwordsWith(sep, lst):
    add = lambda x, y: x + " " + sep + " " + y if x else y
    return str(reduce(add, map(str, lst), ""))

# list(str) -> str
# ['a', 'b', 'c'] -> 'a b c'
def unwords(lst):
    add = lambda x, y: x + " " + y if x else y
    return str(reduce(add, map(str, lst), ""))

