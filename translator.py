
from functools import *
from operator  import *

from ast       import *
from utils     import *

js_keywords = open("js_keywords").read().split()

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
    ".": "dude",
    "`": "quote"
}

def convert_char(char):
    if char in known_ops:
        return "_" + known_ops[char]
    
    if char >= 'A' and char <= 'Z' or char >= 'a' and char <= 'z':
        return char

    return "_" + str(ord(char))

# because, as I said, stdlib/reduce is a bullshit
safe = lambda op: lambda x, y: op(x, y) if x else y

def convert_name(name):
    if name in js_keywords:
        return "_" + name
    else:
        return reduce(safe(add), map(convert_char, name))

def wrapWithCurlyBracets(string):
    return "(function() { " + string + "}) ()"

def convert_ast(ast):
    if of(Nil, ast):
        return "[]";
    
    if of(Var, ast):
        alpha = True

        for c in ast.name[1:]:
            alpha = alpha and (
                c >= 'A' and c <= 'Z' or 
                c >= 'a' and c <= 'z' or
                c >= '0' and c <= '9' or
                c == "_"
            )

        if ast.name[0] == "." and len(ast.name) > 1 and alpha:
            thing = "(call(\"" + ast.name[1:] + "\"))"
            return thing
        else:
            return convert_name(ast.name)
    
    if of(Const, ast):
        if of(str, ast.value):
            return ast.value + '\"'
        return str(ast.value)

    if of(Function, ast):
        return (
              "function (" + unwordsWith(",", map(convert_name, ast.args))
            + ") { return " + convert_ast(ast.body) 
            + " }"
        )

    if of(App, ast):
        if ast.xs:
            return convert_ast(ast.f) + "(" + unwordsWith(",", map(convert_ast, ast.xs)) + ")"
        else:
            return convert_ast(ast.f)

    # let-expression, in fact, is in-place desugared to application:
    # let id = x -> x in id 1 => (id -> id 1) (x -> x)
    # we need an improvement here, using "var" is more preferrable
    if of(LetExpr, ast):
        def unfoldLets(ast):
            if of(LetExpr, ast):
                list, last = unfoldLets(ast.context)
                return ([(ast.name, ast.value)] + list, last)
            return ([], ast)

        bindings, context = unfoldLets(ast)

        def makeVar(name, value):
            converted = convert_ast(value)
            return ("var " + convert_name(name) +
                " = "  + (wrapWithCurlyBracets(converted)
                if of(LetExpr, value)
                else converted))

        vars = map(vararg(makeVar), bindings)

        preface = unwordsWith(";", vars)

        return wrapWithCurlyBracets(preface + " ; return " + convert_ast(context))

    raise "Can't do anything with " + str(ast)

def convert(ast):
    runtime = open("runtime.js").read()

    return runtime + "\n\nvar it = " + convert_ast(ast)

