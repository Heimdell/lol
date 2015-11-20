let uncons = list ret ->
    ret (fst list) (rest list)
in

let x =
    uncons (list 1 2) (head tail ->
    ++ tail (list head))
in

let add = x y -> + x y in

let curry = f x -> y -> f x y in

# comment
let om-nom-nom! = rec (self -> _ -> self) in

let test = curry add "1" in

print (test 2) (_ -> halt ())
