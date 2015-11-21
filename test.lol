
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
           list ;

    case-list? list
        (       ; zero)
        (-> h t ; self (f zero h) t)
in

let reversed =
    -> list ;
    foldl (flip cons) () list
in

let x =
    map (_ + 1) (list 1 2 3)
in

let y =
    foldl + 0 (list 1 2 3)
in

let z = 
    reversed (list 1 2 3)
in

print x ; # prints [ 2, 3, 4 ]
print y ; # prints 6
print z ; # prints [ 3, 2, 1 ]
halt ()
