
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
        return "<" + str(me.value)  + ">"

class App(Ast):
    def __init__(me, info, f, xs):
        me.info = info
        me.f    = f
        me.xs   = xs

    def __str__(me):
        return str(me.f) + " (" + joinWith(", ", me.xs) + ")"

class LetExpr(Ast):
    def __init__(me, info, bindings, context):
        me.info     = info
        me.bindings = bindings
        me.context  = context

    def __str__(me):
        return "\nlet " + unwordsWith("\nand", (map(indent, me.bindings))) + "\nin  " + str(me.context)

def indent(text):
    header, *lines = str(text).split("\n")
    return header + ("\n" if lines else "") + joinWith("\n", map(lambda line: "    " + line, lines))

class Binding(Ast):
    def __init__(me, info, name, type, args, vararg, value):
        me.info   = info
        me.name   = name
        me.type   = type
        me.args   = args
        me.vararg = vararg
        me.value  = value

    def __str__(me):
        return (
            me.name + " :: " + str(me.type) + "\n" +
            me.name + 
            (" " + unwords(me.args) if me.args else "") +
            (" ..." if me.vararg else "") +
            " = " + str(me.value)
        )

class Delayed(Ast):
    def __init__(me, info, thunk):
        me.info  = info
        me.thunk = thunk

    def __str__(me):
        return "(\\" + indent(str(me.thunk)) + ")"


