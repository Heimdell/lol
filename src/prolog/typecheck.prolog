
test 
    :- gt(
        (((a -> b) -> c) -> d) -> e, 
        (((forall(A, A) -> b) -> c) -> d) -> e,
        R
    ),
    (   R = ok
    ->  writeln(ok)
    ;   prepare(R, R1, 0, _)
    ,   maplist(writeln, R1)
    ).

gt(X, Y, R) :- gt(0, X, Y, R).

gt(I, X, Y, R) 
    :-  indent(s(I), X > Y)
    ,   (   cyclic_term(X) -> R = [{infinite, X}]
        ;   cyclic_term(Y) -> R = [{infinite, Y}]
        ;   var(X) -> !, X = Y, R = ok
        ;   var(Y) -> !, Y = X, R = ok
        
        ;   X = Y, R = ok

        ;   X = forall(_, _), Y = forall(_, _)
        ->  copy_term(X, forall(U, Q))
        ,   copy_term(Y, forall(U, W))
        ,   gt(s(I), Q, W, R1)
        ,   ( R1 = ok -> R = ok; append(R1, [{'while unifying', X > Y}], R))

        ;   X = forall(_, _)
        ->  copy_term(X, forall(_, B))
        ,   gt(s(I), B, Y, R1)
        ,   ( R1 = ok -> R = ok; append(R1, [{'while unifying', X > Y}], R))

        ;   X = (A -> B), Y = (C -> D)
        ->  gt(s(I), C, A, R1)
        ,   (   R1 = ok 
            ->  gt(s(I), B, D, R2)
            ,   (   R2 = ok
                ->  R  = ok
                ;   append(R2, [{'while unifying', X > Y}], R)
                )
            ;   append(R1, [{'while unifying', X > Y}], R)
            )

        ;   X =.. [app | ThingsX], Y =.. [app | ThingsY]
        ->  fold(gt(s(I)), ThingsX, ThingsY, R1)
        ,   ( R1 = ok -> R = ok; append(R1, [{'while unifying', X > Y}], R))

        ;   R = [{X, 'not a valid subset of', Y}]
        ).

fold(_, [], [], ok).
fold(F, [X | Xs], [Y | Ys], R)
    :-  call(F, X, Y, R1)
    ,   (   R1 = ok
        ->  fold(F, Xs, Ys, R)
        ;   R = R1
        ).


prepare(X, Y, N, M)
    :-  var(X)
    ->  X = N
    ,   Y = N
    ,   M is N + 1
    
    ;   X =.. [F | ThingsX]
    ,   ThingsX \= []
    ->  foldl(prepare, ThingsX, ThingsY, N, M)
    ,   (F = forall -> F1 = ∀; F1 = F)
    ,   Y =.. [F1 | ThingsY]

    ;   Y = X, M = N
    .

indent(0, M) :- copy_term(M, N), prepare(N, M1, 0, _), writeln(M1).
indent(s(I), M) :- write(' '), indent(I, M).

die(M) 
    :-  writeln(M)
    ,   fail
    .

typecheck(E, X, _)
    :-  die(typecheck(E, X, ?))
    .

typecheck(Env, let(Bindings, Body), Ty)
    :-  foldl(collectBindings, Bindings, Env, Env1)
    ,   typecheck(Env1, Body, Ty)
    .

typecheck(Env, app(Items), Ty)
    :-  maplist(typecheck(Env), Items, [TF | TXs])
    ,   foldl(merge, TXs, TF, Ty)
    .

typecheck(Env, X, T)
    :-  atom(X)
    ,   member(X - T, Env)
    .

typecheck(_, X, int)
    :-  number(X)
    .

merge(TX, TX -> R, R).

lookup(Env, K, V) :- member(K - V, Env).

collectBindings(bind(Name, Args, Value), Env, [Bind | Env])
    :-  Bind = Name - T
    ,   reverse(Args, RArgs)
    ,   foldl(makeArrow, RArgs, ArgsBindings, R, T)
    ,   append([[Bind], ArgsBindings, Env], Env1)
    ,   typecheck(Env1, Value, R)
    .

makeArrow(A, A - T, In, T -> In).

free(A, A - T).
