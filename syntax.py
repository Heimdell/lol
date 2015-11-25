from tokenizer  import *
from parser     import *
from ast        import *
from translator import *
from utils      import *

name = (
    notOneOf([";", "data", "and", "or", "let", "=", "in", "(", ")", "->"])
        .called("name")
)

# program is a let-block or a pure expression
program = recursive(lambda: (
    ( let_block
    | complex
    )
))

let_block = atPoint(lambda point: (
    (listOf
        & the("let")
        & name
        & the("=")
        & program
        & the("in")
        & program)
    .map(vararg(lambda _, name, _1, value, _2, context: (
        LetExpr(point, name, value, context)
    )))
))

# complex is an apllication (print 1 2) or a lambda (x y -> x)
complex = recursive(lambda: (
    (listOf
        # parse many prefixes of the form "x y ->""
        # & many(
        #     (listOf 
        #         & getPosition
        #         & many(name)
        #         & the("->"))
        #     .map(vararg(lambda pos, name, _: (pos, name)))
        # )
        & listOf
        # parse entailing application of the form "f x y ..."
        & (listOf
            & getPosition
            & term
            & many(term))
    )
    .map(vararg(buildAFuncOrApp))
))

# ([[pos1, x, y], [pos2, w, z]], App(pos3, f, [x, y])) 
# -> 
# Function(pos1, [x, y], Function(pos2, [w, z], App(pos3, f, [x, y])))
def buildAFuncOrApp(lambdas, body):
    return foldr(
        lambdas, 
        App(body[0], body[1], body[2]), 
        lambda body, pile: (
            Function(pile[0], pile[1], body)
        )
    )

# parse a terminal value of some kind
term = atPoint(lambda point:
    ( (listOf & the("(") & the(")"))
        .retract() # so it wont yell Expected(nil) on "(+ 1 2)"
        .called("nil")
        .produces(Nil(point))
    
    | regexp("^[0-9][0-9]*\.?[0-9]*$")
        .called("number")
        .map(lambda val: Const(point, int(val)))

    # string are only started with '"' - thanks to the Tokenizer
    | regexp("^\"")
        .called("string")
        .map(lambda val: Const(point, val))

    | name
        .map(lambda name: Var(point, name))
    
    | (listOf & the("(") & program & the(")"))
        .called("expression in brackets")
        .map(vararg(lambda _, it, _1: it))

    | (listOf 
        & the("->") 
        & many1(name) 
        & the(";") 
        & program)
        .map(vararg(lambda _, args, _1, body: Function(point, args, body)))

    | (listOf 
        & the(";") 
        & program)
        .map(vararg(lambda _, body: Function(point, [], body)))
    )
)

whole_program = (
    (listOf 
        & program 
        & eof)
    .map(vararg(
        lambda prog, _: prog
    ))
)
