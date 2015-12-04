
from tokenizer  import *
from parser     import *
from ast        import *
from translator import *
from utils      import *

name = (
    notOneOf(["...", "val", "fun", "=", "in", "\\"])
    .called("name")
)

whole_program = deferred(lambda: (
    (listOf
        & program
        & eof)

    .map(vararg(lambda it, _: it))
))

program = deferred(lambda: (
    ( application.called("application")
    | let_expr
    | delayed
    )
))

let_expr = deferred(lambda: (
    (listOf
        & getPosition
        & bindings
        & "in"
        & program)

    .map(vararg(lambda point, bindings, _, context: (
        LetExpr(point, bindings, context)
    )))
))

bindings = deferred(lambda: (
    ( (listOf
        & binding
        & bindings)
        .map(vararg(lambda x, xs: [x] + xs))
    | pure([])
    )
))

binding = deferred(lambda: (
    ( (listOf
        & getPosition
        & "val"
        & name
        & "="
        & program)
        .map(vararg(lambda point, _val, name, _, value: (
            Binding(point, name, None, [], None, value)
        )))

    | (listOf
        & getPosition
        & "fun"
        & name
        & many1(name)
        & (the("...") | pure(None))
        & "="
        & program)
        .map(vararg(lambda point, _fun, name, args, vararg, _, value: (
            Binding(point, name, None, args, vararg, value)
        )))
    )
))

application = deferred(lambda: (
    (listOf
        & getPosition
        & term
        & many(term))

        .map(vararg(lambda point, f, xs: (
            f if empty(xs) else App(point, f, xs)
        )))
))

term = deferred(lambda: const | var)

delayed = deferred(lambda: (
    (listOf
        & getPosition
        & the("\\").called("\-thunk")
        & program)

    .map(vararg(lambda point, _, it: Delayed(point, it)))
))

const = deferred(lambda: (
    (listOf
        & getPosition
        & ( regexp("^[0-9][0-9]*\.?[0-9]*$")
            .map(int)
          
          | regexp("^\"")
            .map(lambda it: it + '"')
          ))
    
    .map(vararg(lambda point, it: Const(point, it)))
))

var = deferred(lambda: (
    (listOf
        & getPosition
        & name
          .called("name"))
          .map(vararg(lambda point, name: Var(point, name)))
))
