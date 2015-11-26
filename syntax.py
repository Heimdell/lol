from tokenizer  import *
from parser     import *
from ast        import *
from translator import *
from utils      import *

name = (
    notOneOf(["...", "data", "and", "or", "let", "=", "in", "(", ")", "\\"])
    .called("name")
)

'''
    program     ::= let-expr | application | const | var
    let-expr    ::= "let" bindings "in" program
    bindings    ::= binding ("and" binding)*
    application ::= name program*
'''

whole_program = recursive(lambda: (
    (listOf
        & program
        & eof)

    .map(vararg(lambda it, _: it))
))

program = recursive(lambda: (
    ( application
    | let_expr
    | delayed
    )
))

let_expr = atPoint(lambda point: (
    (listOf
        & "let"
        & bindings
        & "in"
        & program)

    .map(vararg(lambda _, bindings, _1, context: (
        LetExpr(point, bindings, context)
    )))
))

bindings = recursive(lambda: (
    (listOf
        & binding
        & many(
            (listOf
                & "and"
                & binding)

            .map(vararg(lambda _, binding: binding))))

    .map(vararg(lambda fst, rest: (
        [fst] + rest
    )))
))

binding = atPoint(lambda point: (
    (listOf
        & name
        & many(name)
        & (the("...") | pure(False))
        & "="
        & program)

    .map(vararg(lambda name, args, vararg, _, value: (name, args, bool(vararg), value)))
))

application = atPoint(lambda point: (
    (listOf
        & var
        & many(term))

    .map(vararg(lambda f, xs: (
        f if empty(xs) else App(point, f, xs)
    )))
))

term = recursive(lambda: const | var)

delayed = atPoint(lambda point: (
    (listOf
        & "\\"
        & program)

    .map(vararg(lambda _, it: Delayed(point, it)))
))

const = atPoint(lambda point: (
    ( regexp("^[0-9][0-9]*\.?[0-9]*$").map(int)
    | regexp("^\"").map(lambda it: it + '"')
    )
    .map(lambda it: Const(point, it))
))

var = atPoint(lambda point:
    name
    .called("name")
    .map(lambda name: Var(point, name))
)
