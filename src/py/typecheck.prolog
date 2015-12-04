
test 
    :- gt(
        ((app(list, i) -> o) -> (app(list, forall(I, I)) -> o)) -> o, 
        forall(A, A -> A) -> o
    ).

gt(X, Y) :- gt(0, X, Y).

gt(I, X, Y) 
    :-  indent(s(I), X > Y)
    ,   (   var(X) -> !, X = Y
        ;   var(Y) -> !, Y = X
        
        ;   X = forall(_, _), Y = forall(_, _)
        ->  copy_term(X, forall(U, Q))
        ,   copy_term(Y, forall(U, W))
        ,   gt(s(I), Q, W)

        ;   X = forall(_, _)
        ->  copy_term(X, forall(_, B))
        ,   gt(s(I), B, Y)

        ;   X = (A -> B), Y = (C -> D)
        ->  gt(s(I), B, D)
        ,   gt(s(I), C, A)

        ;   X =.. [app | ThingsX], Y =.. [app | ThingsY]
        ->  map(gt(s(I)), ThingsX, ThingsY)

        ;   X = Y

        ;   indent(s(I), {X, 'not a valid subset of', Y})
        ,   fail
        )
    .

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

map(_, X, Y) :- die(X - Y).
map(F, Seq1, Seq2) :- maplist(F, Seq1, Seq2).
map(F, (A, Seq1), (B, Seq2)) :-
    call(F, A, B),
    map(F, Seq1, Seq2).
map(F, A, B) :- call(F, A, B).