
let ` = list in

# perfrom case-analisys on list
let case-list? =
    -> list on-nil on-cons ;
    ? (null? list)
          on-nil
        ; on-cons (fst list) (rest list)
in

let flip =
    -> f   ;
    -> x y ;
    f y x
in

# curry a function
let _ =
    -> f x ; # firstly, receive function & 1st param
    -> y   ; # then, receive 2nd param
    f x y    # call the function
in

# uncurry the function
let uncurried =
    -> f ;   # get the function
    -> x y ; # get all args
    (f x) y  # feed them by one
in

# uncurry the function
let uncurried3 =
    -> f ;     # get the function
    -> x y z ; # get all args
    (f x) y z  # feed them by one
in

# glue an x in front of xs
let cons =
    -> x xs ;
    ++ (list x) xs
in

let map = uncurried # "rec" separates arguments, making it curried
                    # so, we have to undo that effect
        -> f    ;   # get a function to apply
    rec -> self ;   # from there we're recursive
        -> list ;
    
    case-list? list
        (             ; ()) 
        (-> head tail ; cons (f head) (self tail))
in

let foldl = uncurried3
        -> f    ;
    rec -> self ;
        -> zero
           lst ;
    case-list? lst
        (       ; zero)
        (-> h t ; self (f zero h) t)
in

let reversed =
    -> list ;
    foldl (flip cons) () list
in

# vararg function, calling foldl on its arglist
let folds-args =
           -> op zero ; # receive config
    vararg -> list    ; # reveive arg list
    foldl op zero list
in

# vararg-sum
let sum = folds-args + 0 in

# compose 2 functions
let . =
    -> f g ;
    -> x   ;
    f (g x)
in

let .: =
    -> f g ;
    -> x y ;
    f (g x) (g y)
in

# compose N functions
let ... =
    folds-args . -> x ; x
in

let x =
    map (... (_ + 1) (_ + 2) (_ + 3))
        (list 1 2 3)
in

let y =
    foldl + 0 (list 1 2 3)
in

let z = 
    reversed (list 1 2 3)
in

let put =
    -> lst ret ;
    print (foldl + "" lst) ret
in

put (` "x = " x) ; # prints [ 2, 3, 4 ]
put (` "y = " y) ; # prints 6
put (` "z = " z) ; # prints [ 3, 2, 1 ]
put (` "(sum 1 2 3 4) = " (sum 1 2 3 4)) ;
put (` "(apply sum (list 1 2 3 4) = " (apply sum (list 1 2 3 4))) ;
halt ()
