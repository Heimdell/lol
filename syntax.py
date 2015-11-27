from tokenizer  import *
from parser     import *
from ast        import *
from translator import *
from utils      import *

name = (
    notOneOf(["...", "and", "let", "=", "in", "\\"])
    .called("name")
)

whole_program = recursive(lambda: (
    (listOf
        & program
        & eof)

    .map(vararg(lambda it, _: it))
))

program = recursive(lambda: (
    ( application.called("application")
    | let_expr
    | delayed
    )
))

let_expr = atPoint(lambda point: (
    (listOf
        & the("let").called("let-expression")
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
        & bindings_cont)

    .map(vararg(lambda fst, rest: (
        [fst] + rest
    )))
))

bindings_cont = recursive(lambda: (
    ( (listOf 
        & "and"
        & binding
        & bindings_cont)
        .map(vararg(lambda _, it, rest: [it] + rest))
    | pure([])
    )
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
        & the("\\").called("\-thunk")
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
