from tokenizer  import *
from parser     import *
from ast        import *
from translator import *
from utils      import *

name = (
    notOneOf(["...", "val", "fun", "=", "in", "\\"])
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
        & bindings
        & "in"
        & program)

    .map(vararg(lambda bindings, _1, context: (
        LetExpr(point, bindings, context)
    )))
))

bindings = recursive(lambda: (
    ( (listOf
        & binding
        & bindings)
        .map(vararg(lambda x, xs: [x] + xs))
    | pure([])
    )
))

binding = atPoint(lambda point: (
    ( (listOf
        & "val"
        & name
        & "="
        & program)
        .map(vararg(lambda _val, name, _, value: (
            Binding(point, name, None, [], None, value)
        )))
    | (listOf
        & "fun"
        & name
        & many1(name)
        & (the("...") | pure(None))
        & "="
        & program)
        .map(vararg(lambda _fun, name, args, vararg, _, value: (
            Binding(point, name, None, args, vararg, value)
        )))
    )

))

application = atPoint(lambda point: (
    ( const

    | (listOf
        & var
        & many(term))

        .map(vararg(lambda f, xs: (
            f if empty(xs) else App(point, f, xs)
        )))
    )
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
