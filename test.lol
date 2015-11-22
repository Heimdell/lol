
# perfom case-analisys on list
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
    -> f   ; # get the function
    -> x y ; # get all args
    (f x) y  # feed them by one
in

# uncurry the function
let uncurried3 =
    -> f     ; # get the function
    -> x y z ; # get all args
    (f x) y z  # feed them by one
in

# glue an x in front of xs
let cons =
    -> x xs ;
    ++ (` x) xs
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
           lst  ;
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
let sum = 
    vararg -> list ;
    case-list? (reversed list)
        (       ; list) 
        (-> h t ; foldl2 + h t)
in

# compose 2 functions
let . =
    -> f g ;
    -> x   ;
    f (g x)
in

# compose N functions
let ... =
    folds-args . (-> x ; x)
in

let x =
    map (... (_ + 1) (_ + 2) (_ + 3))
        (` 1 2 3)
in

let y =
    foldl + 0 (` 1 2 3)
in

let z = 
    reversed (` 1 2 3)
in

let put =
    -> lst ret ;
    print (foldl + "" lst) ret
in

let foldl2 =
    -> op zero list ;
    loop zero list 
      -> zero list recur ;
        case-list? list
            (       ; zero)
            (-> h t ; recur (op h zero) t)
in

let make-pos =
    -> file row col ;
    box
        "file" file
        "row"  row
        "col"  col
in

let count =
    -> pos char ;
    ? (equal? char '\n')
        (; make-pos 
                 (at "file" pos)
            (+ 1 (at "row"  pos))
            1)

        (; make-pos 
                 (at "file" pos)
                 (at "row" pos)
            (+ 1 (at "col" pos)))
in

let pos-str =
    -> pos ;
    sum 
        "{"  (at "file" pos) 
        ", " (at "row" pos) 
        "-"  (at "col" pos) 
        "}"
in

let tokenize =
    -> string ;
    let handler =
        -> char state ; 
        state
    in
    let state =
        box ()
    in
    foldl2 handler state string
in

put (` "x = " (s x)) ;
put (` "y = " y) ;
put (` "z = " (s z)) ;
put (` "(sum 1 2 3 4) = " (sum 1 2 3 4)) ;
put (` "(apply sum (` 1 2 3 4) = " (apply sum (` 1 2 3 4))) ;
put (` (foldl2 + 0 (` 1 2 3 4))) ;
print (pos-str (make-pos "lol.txt" 5 12)) ;
halt ()
